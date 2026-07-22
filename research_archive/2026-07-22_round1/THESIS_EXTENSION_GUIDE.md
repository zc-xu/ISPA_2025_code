# Thesis Extension Guide

The current repository provides a stable two-stage MEC optimization baseline. The following modules can extend it without discarding the original experiments.

## Recommended Extension Points

### 1. Dynamic Service Demand

Add time-indexed requests, service popularity drift, and server reconfiguration cost. Keep the existing static problem as the `t=0` benchmark and compare dynamic policies against repeated static re-optimization.

Primary integration points:

- `LocalSearch/nsga_service_deploy.py`
- `LocalSearch/compute_delay.py`
- `LocalSearch/experiment_configs.py`

### 2. Learning-Based Baselines

The current DQN implementation is a preference-conditioned point-solution baseline. A thesis module can add multi-objective RL, graph neural policies, or actor-critic methods that emit a set of trade-off solutions. Preserve the existing DQN protocol as the simplest learning baseline.

Primary integration point:

- `LocalSearch/dqn_service_baseline.py`

### 3. Joint and Hierarchical Optimization

Use `LocalSearch/joint_optimality_gap.py` as the small-instance oracle. Candidate extensions include decomposition with feedback from Stage II to Stage I, bilevel optimization, or adaptive server relocation. Always retain exact enumeration on small instances as a correctness check.

### 4. Geographical and Traffic Generalization

Extend the alternate-region experiment with authorized station pools, synthetic clustered/uniform/skewed generators, and larger candidate sets. Report both topology statistics and outcome metrics so improvements cannot be attributed only to an easier geography.

Primary integration points:

- `LocalSearch/real_region_generalization.py`
- `LocalSearch/run_real_region_stage2.py`
- `LocalSearch/reviewer6_generalization_summary.py`

### 5. Robustness and Uncertainty

Model uncertain request rates, link delay, server failures, and cost variation. Evaluate expected performance together with worst-case or risk-sensitive metrics.

### 6. Scalability and Systems Evaluation

Add runtime, memory, parallel evaluation, and convergence-budget studies. Keep the existing configuration manifest so every result records candidate count, users, servers, service types, capacity, seed, population size, and generation count.

## Research Hygiene

- Create one machine-readable manifest per experiment family.
- Store raw stochastic runs in NPZ/CSV and derive plots from those files.
- Record seeds and normalization bounds next to every Pareto metric.
- Never select a seed after inspecting only the desired method; use a declared protocol or report multiple seeds.
- Keep response-only diagnostics separate from main-paper evidence.
- Preserve each submitted manuscript and response as a dated snapshot.
- Use Conventional Commits so code, data, and documentation changes remain distinguishable.
