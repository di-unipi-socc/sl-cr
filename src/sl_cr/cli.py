"""Command-line entrypoint for SL-CR experiment grids."""

from __future__ import annotations

from pathlib import Path
from time import time
from typing import Any

from swiplserver import PrologMQI

from sl_cr.app_builder import AppBuilder
from sl_cr.config import DEFAULT_RESULTS_DIR
from sl_cr.experiment import Experiment
from sl_cr.infr_builder import InfrBuilder
from sl_cr.policies import get_policies
from sl_cr.search_space import (
    fixed_config,
    ray_search_space,
)


def sl_cr_grid(config: dict[str, Any]):
    """Run one Ray Tune trial."""

    run_experiment(config, _trial_output_path())


def run_experiment(config: dict[str, Any], path: Path):
    """Run one experiment with an already resolved config dict."""

    application = AppBuilder(
        components=config["components"],
        component_storage=config["component_storage"],
    ).build()
    infrastructure = InfrBuilder(
        topology=config["topology"],
        nodes=config["nodes"],
        node_storage=config["node_storage"],
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

    import ray
    from ray import tune

    ray.init(address="auto")
    start_time = time()
    ray_run_config = tune.RunConfig(storage_path=DEFAULT_RESULTS_DIR.resolve())
    tuner = tune.Tuner(
        tune.with_resources(sl_cr_grid, {"cpu": 2}),
        param_space=ray_search_space(),
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
    from ray import tune

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
