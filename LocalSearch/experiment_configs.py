from collections import OrderedDict


EXPERIMENT_CONFIGS = OrderedDict(
    [
        (
            "10_100",
            {
                "data_file": "data/input_data_10_100_8.xlsx",
                "target_servers": 10,
                "sigma_min": 12,
                "n2_adjust": 0,
                "series": "fixed_servers",
                "users": 100,
            },
        ),
        (
            "10_130",
            {
                "data_file": "data/input_data_10_130_8_new.xlsx",
                "target_servers": 10,
                "sigma_min": 16,
                "n2_adjust": -1,
                "series": "fixed_servers_and_fixed_users",
                "users": 130,
            },
        ),
        (
            "10_150",
            {
                "data_file": "data/input_data_10_150_8_new.xlsx",
                "target_servers": 10,
                "sigma_min": 18,
                "n2_adjust": -1,
                "series": "fixed_servers",
                "users": 150,
            },
        ),
        (
            "10_180",
            {
                "data_file": "data/input_data_10_180_8_new.xlsx",
                "target_servers": 10,
                "sigma_min": 22,
                "n2_adjust": 0,
                "series": "fixed_servers",
                "users": 180,
            },
        ),
        (
            "5_130",
            {
                "data_file": "data/input_data_5_130_8_new.xlsx",
                "target_servers": 5,
                "sigma_min": 15,
                "n2_adjust": -1,
                "series": "fixed_users",
                "users": 130,
            },
        ),
        (
            "15_130",
            {
                "data_file": "data/input_data_15_130_8_new.xlsx",
                "target_servers": 15,
                "sigma_min": 17,
                "n2_adjust": 0,
                "series": "fixed_users",
                "users": 130,
            },
        ),
        (
            "20_130",
            {
                "data_file": "data/input_data_20_130_8_new.xlsx",
                "target_servers": 20,
                "sigma_min": 18,
                "n2_adjust": 0,
                "series": "fixed_users",
                "users": 130,
            },
        ),
    ]
)


def select_configs(names):
    if not names or names == ["all"]:
        return EXPERIMENT_CONFIGS

    selected = OrderedDict()
    missing = []
    for name in names:
        if name in EXPERIMENT_CONFIGS:
            selected[name] = EXPERIMENT_CONFIGS[name]
        else:
            missing.append(name)

    if missing:
        known = ", ".join(EXPERIMENT_CONFIGS.keys())
        raise ValueError(f"Unknown config(s): {', '.join(missing)}. Known configs: {known}")

    return selected
