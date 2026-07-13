import argparse
import glob
import os
import random
import sys
from collections import deque

import numpy as np
import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from LocalSearch.compute_delay import SERVICE_CAPACITY_PER_SERVER, SERVICE_DEPLOY_COSTS
from LocalSearch.experiment_configs import select_configs
from LocalSearch.experiment_utils import build_stage_context
from LocalSearch.nsga_service_deploy import MyServiceDeployProblem


BASELINE_FILES = (
    "res_random",
    "res_greedy_cost",
    "res_greedy_request",
    "res_hybrid-A-1",
)


def ensure_dirs():
    for rel in ("output/npz", "output/csv"):
        os.makedirs(os.path.join(PROJECT_ROOT, rel), exist_ok=True)


def nondominated_mask(points):
    points = np.asarray(points, dtype=float)
    keep = np.ones(len(points), dtype=bool)
    for i, point in enumerate(points):
        dominated = np.all(points <= point, axis=1) & np.any(points < point, axis=1)
        if np.any(dominated):
            keep[i] = False
    return keep


def reference_bounds(config_name):
    arrays = []
    npz_dir = os.path.join(PROJECT_ROOT, "output", "npz")
    for stem in BASELINE_FILES:
        candidates = [os.path.join(npz_dir, f"{stem}_{config_name}.npz")]
        if config_name == "10_130":
            candidates.append(os.path.join(npz_dir, f"{stem}.npz"))
        path = next((item for item in candidates if os.path.exists(item)), None)
        if path:
            with np.load(path) as result:
                arrays.append(np.asarray(result["F"], dtype=float))
    if not arrays:
        raise FileNotFoundError(f"No Stage II reference results found for {config_name}.")
    combined = np.vstack(arrays)
    return np.min(combined, axis=0), np.max(combined, axis=0)


class ServicePlacementEnv:
    def __init__(self, context, problem, weight, lower, upper, seed):
        self.context = context
        self.problem = problem
        self.weight = float(weight)
        self.lower = np.asarray(lower, dtype=float)
        self.upper = np.asarray(upper, dtype=float)
        self.rng = np.random.default_rng(seed)
        self.k = int(context["k"])
        self.num_services = len(SERVICE_DEPLOY_COSTS)
        self.capacity = int(SERVICE_CAPACITY_PER_SERVER)
        self.action_count = self.num_services + 1

        assigned = np.asarray(context["assigned_server"], dtype=int)
        services = np.asarray(context["user_services"], dtype=int)
        self.local_requests = np.zeros((self.k, self.num_services), dtype=float)
        for server, service in zip(assigned, services):
            self.local_requests[server, service] += 1.0
        row_sum = np.maximum(self.local_requests.sum(axis=1, keepdims=True), 1.0)
        self.local_requests /= row_sum
        self.global_requests = np.bincount(services, minlength=self.num_services).astype(float)
        self.global_requests /= max(self.global_requests.sum(), 1.0)
        costs = np.asarray(SERVICE_DEPLOY_COSTS, dtype=float)
        self.cost_features = costs / max(costs.max(), 1.0)
        self.reset()

    @property
    def state_dim(self):
        return 3 + 4 * self.num_services

    def reset(self):
        self.matrix = np.zeros((self.k, self.num_services), dtype=np.int8)
        self.server = 0
        self.slot = 0
        self.done = False
        return self.state()

    def state(self):
        server_scale = self.server / max(self.k - 1, 1)
        slot_scale = self.slot / max(self.capacity - 1, 1)
        selected = self.matrix[min(self.server, self.k - 1)].astype(float)
        return np.concatenate(
            [
                np.array([server_scale, slot_scale, self.weight], dtype=float),
                selected,
                self.local_requests[min(self.server, self.k - 1)],
                self.cost_features,
                self.global_requests,
            ]
        ).astype(np.float32)

    def valid_actions(self):
        mask = np.ones(self.action_count, dtype=bool)
        if self.done:
            return mask
        mask[: self.num_services] = self.matrix[self.server] == 0
        return mask

    def _advance(self):
        self.slot += 1
        if self.slot >= self.capacity:
            self.slot = 0
            self.server += 1
        if self.server >= self.k:
            self.done = True

    def step(self, action):
        if self.done:
            raise RuntimeError("Episode has already terminated.")
        action = int(action)
        request_gain = 0.0
        deploy_penalty = 0.0
        if action < self.num_services and self.matrix[self.server, action] == 0:
            self.matrix[self.server, action] = 1
            request_gain = self.local_requests[self.server, action]
            deploy_penalty = self.cost_features[action]

        shaped = 0.08 * ((1.0 - self.weight) * request_gain - self.weight * deploy_penalty)
        self._advance()
        objective = None
        if self.done:
            cost, delay = self.problem._calc_obj(self.matrix)
            objective = np.array([cost, delay], dtype=float)
            normalized = (objective - self.lower) / np.maximum(self.upper - self.lower, 1e-12)
            scalar = self.weight * normalized[0] + (1.0 - self.weight) * normalized[1]
            missing = np.count_nonzero(self.matrix.sum(axis=0) == 0)
            shaped += 2.0 - 4.0 * scalar - 0.5 * missing
            next_state = np.zeros(self.state_dim, dtype=np.float32)
        else:
            next_state = self.state()
        return next_state, float(shaped), self.done, objective


class NumpyDQN:
    def __init__(self, state_dim, action_dim, seed=42, hidden=64, learning_rate=7e-4, gamma=0.98):
        self.rng = np.random.default_rng(seed)
        self.gamma = float(gamma)
        self.learning_rate = float(learning_rate)
        self.w1 = self.rng.normal(0.0, np.sqrt(2.0 / state_dim), (state_dim, hidden))
        self.b1 = np.zeros(hidden)
        self.w2 = self.rng.normal(0.0, np.sqrt(2.0 / hidden), (hidden, action_dim))
        self.b2 = np.zeros(action_dim)
        self.target = self.copy_weights()

    def copy_weights(self):
        return tuple(item.copy() for item in (self.w1, self.b1, self.w2, self.b2))

    def sync_target(self):
        self.target = self.copy_weights()

    @staticmethod
    def forward_with(states, weights):
        w1, b1, w2, b2 = weights
        z1 = states @ w1 + b1
        hidden = np.maximum(z1, 0.0)
        return hidden @ w2 + b2, z1, hidden

    def q_values(self, state):
        q, _, _ = self.forward_with(np.asarray(state, dtype=float)[None, :], self.copy_weights())
        return q[0]

    def act(self, state, valid_mask, epsilon):
        valid = np.flatnonzero(valid_mask)
        if self.rng.random() < epsilon:
            return int(self.rng.choice(valid))
        q = self.q_values(state).copy()
        q[~valid_mask] = -np.inf
        return int(np.argmax(q))

    def train(self, batch):
        states = np.asarray([row[0] for row in batch], dtype=float)
        actions = np.asarray([row[1] for row in batch], dtype=int)
        rewards = np.asarray([row[2] for row in batch], dtype=float)
        next_states = np.asarray([row[3] for row in batch], dtype=float)
        dones = np.asarray([row[4] for row in batch], dtype=float)
        next_masks = np.asarray([row[5] for row in batch], dtype=bool)

        q, z1, hidden = self.forward_with(states, self.copy_weights())
        next_q, _, _ = self.forward_with(next_states, self.target)
        next_q[~next_masks] = -1e9
        targets = rewards + self.gamma * (1.0 - dones) * np.max(next_q, axis=1)
        predictions = q[np.arange(len(batch)), actions]
        error = np.clip(predictions - targets, -5.0, 5.0)

        grad_q = np.zeros_like(q)
        grad_q[np.arange(len(batch)), actions] = error / len(batch)
        grad_w2 = hidden.T @ grad_q
        grad_b2 = grad_q.sum(axis=0)
        grad_hidden = grad_q @ self.w2.T
        grad_z1 = grad_hidden * (z1 > 0)
        grad_w1 = states.T @ grad_z1
        grad_b1 = grad_z1.sum(axis=0)

        for grad in (grad_w1, grad_b1, grad_w2, grad_b2):
            np.clip(grad, -2.0, 2.0, out=grad)
        self.w1 -= self.learning_rate * grad_w1
        self.b1 -= self.learning_rate * grad_b1
        self.w2 -= self.learning_rate * grad_w2
        self.b2 -= self.learning_rate * grad_b2
        return float(np.mean(error**2))


def run_episode(env, agent, epsilon, replay=None, batch_size=64, train=False):
    state = env.reset()
    total_reward = 0.0
    losses = []
    objective = None
    while True:
        valid = env.valid_actions()
        action = agent.act(state, valid, epsilon)
        next_state, reward, done, objective = env.step(action)
        next_mask = np.ones(env.action_count, dtype=bool) if done else env.valid_actions()
        if replay is not None:
            replay.append((state.copy(), action, reward, next_state.copy(), done, next_mask.copy()))
            if train and len(replay) >= batch_size:
                indices = agent.rng.choice(len(replay), size=batch_size, replace=False)
                batch = [replay[int(index)] for index in indices]
                losses.append(agent.train(batch))
        state = next_state
        total_reward += reward
        if done:
            break
    return env.matrix.copy(), objective, total_reward, float(np.mean(losses)) if losses else np.nan


def train_one(config_name, config, context, weight, dqn_seed, args, lower, upper):
    random.seed(dqn_seed)
    np.random.seed(dqn_seed)
    problem = MyServiceDeployProblem(
        k=context["k"],
        servers_pos=context["servers_pos"],
        user_positions=context["user_positions"],
        user_services=context["user_services"],
        assigned_server=context["assigned_server"],
    )
    env = ServicePlacementEnv(context, problem, weight, lower, upper, dqn_seed)
    agent = NumpyDQN(
        env.state_dim,
        env.action_count,
        seed=dqn_seed,
        hidden=args.hidden,
        learning_rate=args.learning_rate,
        gamma=args.gamma,
    )
    replay = deque(maxlen=args.replay_size)
    log_rows = []
    best = None
    for episode in range(args.episodes):
        fraction = episode / max(args.episodes - 1, 1)
        epsilon = args.epsilon_end + (args.epsilon_start - args.epsilon_end) * np.exp(-5.0 * fraction)
        matrix, objective, reward, loss = run_episode(
            env, agent, epsilon, replay=replay, batch_size=args.batch_size, train=True
        )
        normalized = (objective - lower) / np.maximum(upper - lower, 1e-12)
        scalar = weight * normalized[0] + (1.0 - weight) * normalized[1]
        if best is None or scalar < best[0]:
            best = (float(scalar), matrix.copy(), objective.copy(), episode)
        if (episode + 1) % args.target_sync == 0:
            agent.sync_target()
        log_rows.append(
            {
                "Config": config_name,
                "Weight": weight,
                "Seed": dqn_seed,
                "Episode": episode + 1,
                "Epsilon": epsilon,
                "Reward": reward,
                "Loss": loss,
                "Cost": objective[0],
                "Delay": objective[1],
                "ScalarQ": scalar,
                "BestScalarQ": best[0],
            }
        )

    matrix, objective, _, _ = run_episode(env, agent, epsilon=0.0)
    normalized = (objective - lower) / np.maximum(upper - lower, 1e-12)
    scalar = weight * normalized[0] + (1.0 - weight) * normalized[1]
    if scalar < best[0]:
        best = (float(scalar), matrix.copy(), objective.copy(), args.episodes)
    return best, log_rows


def run_config(config_name, config, args):
    print(f"\n=== DQN config {config_name} ===")
    context = build_stage_context(
        config,
        seed=args.stage_seed,
        coverage_radius=args.coverage_radius,
        max_iter=args.stage1_iter,
        verbose=False,
    )
    lower, upper = reference_bounds(config_name)
    print(f"K={context['k']}, users={len(context['user_positions'])}, bounds={lower}..{upper}")
    solutions = []
    objectives = []
    summary_rows = []
    training_rows = []
    for dqn_seed in args.dqn_seeds:
        for weight in args.weights:
            best, rows = train_one(
                config_name, config, context, weight, dqn_seed, args, lower, upper
            )
            scalar, matrix, objective, episode = best
            solutions.append(matrix.reshape(-1))
            objectives.append(objective)
            training_rows.extend(rows)
            summary_rows.append(
                {
                    "Config": config_name,
                    "Weight": weight,
                    "Seed": dqn_seed,
                    "BestEpisode": episode + 1,
                    "Cost": objective[0],
                    "Delay": objective[1],
                    "ScalarQReferenceBounds": scalar,
                }
            )
            print(
                f"weight={weight:.2f}, seed={dqn_seed}: cost={objective[0]:.4f}, "
                f"delay={objective[1]:.4f}, q={scalar:.4f}"
            )

    X = np.asarray(solutions, dtype=np.int8)
    F = np.asarray(objectives, dtype=float)
    keep = nondominated_mask(F)
    path = os.path.join(PROJECT_ROOT, "output", "npz", f"res_dqn_{config_name}.npz")
    np.savez(
        path,
        X=X,
        F=F,
        pareto_X=X[keep],
        pareto_F=F[keep],
        weights=np.asarray(args.weights, dtype=float),
        seeds=np.asarray(args.dqn_seeds, dtype=int),
        episodes=np.asarray([args.episodes], dtype=int),
    )
    if config_name == "10_130":
        np.savez(
            os.path.join(PROJECT_ROOT, "output", "npz", "res_dqn.npz"),
            X=X,
            F=F,
            pareto_X=X[keep],
            pareto_F=F[keep],
            weights=np.asarray(args.weights, dtype=float),
            seeds=np.asarray(args.dqn_seeds, dtype=int),
            episodes=np.asarray([args.episodes], dtype=int),
        )

    summary_path = os.path.join(PROJECT_ROOT, "output", "csv", f"dqn_summary_{config_name}.csv")
    training_path = os.path.join(PROJECT_ROOT, "output", "csv", f"dqn_training_{config_name}.csv")
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
    pd.DataFrame(training_rows).to_csv(training_path, index=False)
    print(f"Saved {path}")
    return summary_rows


def parse_args():
    parser = argparse.ArgumentParser(description="Reproducible DQN baseline for Stage II service placement.")
    parser.add_argument("--configs", nargs="+", default=["10_130"])
    parser.add_argument("--weights", nargs="+", type=float, default=[0.1, 0.3, 0.5, 0.7, 0.9])
    parser.add_argument("--dqn-seeds", nargs="+", type=int, default=[42])
    parser.add_argument("--episodes", type=int, default=320)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=7e-4)
    parser.add_argument("--gamma", type=float, default=0.98)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--replay-size", type=int, default=12000)
    parser.add_argument("--target-sync", type=int, default=20)
    parser.add_argument("--epsilon-start", type=float, default=1.0)
    parser.add_argument("--epsilon-end", type=float, default=0.05)
    parser.add_argument("--stage-seed", type=int, default=42)
    parser.add_argument("--coverage-radius", type=float, default=1.5)
    parser.add_argument("--stage1-iter", type=int, default=200)
    return parser.parse_args()


def main():
    args = parse_args()
    if any(weight < 0.0 or weight > 1.0 for weight in args.weights):
        raise ValueError("All weights must be within [0, 1].")
    ensure_dirs()
    selected = select_configs(args.configs)
    for config_name, config in selected.items():
        run_config(config_name, config, args)
    frames = []
    pattern = os.path.join(PROJECT_ROOT, "output", "csv", "dqn_summary_*.csv")
    for path in sorted(glob.glob(pattern)):
        if os.path.basename(path) != "dqn_summary_all_control_configs.csv":
            frames.append(pd.read_csv(path))
    all_rows = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    all_path = os.path.join(PROJECT_ROOT, "output", "csv", "dqn_summary_all_control_configs.csv")
    all_rows.to_csv(all_path, index=False)
    print(f"Saved {all_path}")


if __name__ == "__main__":
    main()
