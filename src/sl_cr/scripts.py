"""Command-line entrypoint for SL-CR experiment grids."""

from __future__ import annotations

from pathlib import Path
from time import time
from typing import Any

import ray
from ray import tune
from swiplserver import PrologMQI

from sl_cr.builders.application import AppBuilder
from sl_cr.builders.infrastructure import InfrBuilder
from sl_cr.config import DEFAULT_RESULTS_DIR
from sl_cr.experiment import Experiment
from sl_cr.policies import get_policies
from sl_cr.search_space import (
    complete_search_space,
    debug_search_space,
    fixed_config,
)


def sl_cr_grid(config: dict[str, Any]):
    """Run one Ray Tune trial."""

    run_experiment(config, _trial_output_path())


def run_experiment(config: dict[str, Any], path: Path):
    """Run one experiment with an already resolved config dict."""

    application = AppBuilder(
        components=config["components"],
        seed=config["seed"],
    ).build()
    infrastructure = InfrBuilder(
        topology=config["topology"],
        nodes=config["nodes"],
        seed=config["seed"],
        update_policies=get_policies(),
    ).build()

    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog:
            Experiment(
                infrastructure=infrastructure,
                application=application,
                prolog_thread=prolog,
                config=config,
                mode=config["mode"],
                output_path=path,
            ).run()


def main():
    """Run the Ray Tune grid."""

    ray.init(address="auto")

    start_time = time()
    ray_run_config = tune.RunConfig(storage_path=DEFAULT_RESULTS_DIR.resolve())
    tuner = tune.Tuner(
        tune.with_resources(sl_cr_grid, {"cpu": 4}),
        # sl_cr_grid,
        param_space=complete_search_space(),
        run_config=ray_run_config,
    )
    tuner.fit()
    print("Elapsed time: ", time() - start_time)


def debug():
    """Run one local experiment without Ray Tune."""

    start_time = time()
    output_path = DEFAULT_RESULTS_DIR / "debug" / "output"
    run_experiment(fixed_config, output_path)
    print("Elapsed time: ", time() - start_time)


def _trial_output_path() -> Path:

    context = tune.get_context()
    storage = context.get_storage()
    if storage is None:
        return DEFAULT_RESULTS_DIR / "local" / "output"
    return (
        Path(storage.storage_fs_path)
        / storage.experiment_dir_name
        / str(storage.trial_dir_name)
        / "output"
    )
