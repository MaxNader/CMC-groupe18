
from util.run_closed_loop import run_multiple
from util.run_closed_loop import run_single
from simulation_parameters import SimulationParameters
import os
from plotting_common import plot_left_right, plot_trajectory, plot_time_histories, plot_time_histories_multiple_windows
import numpy as np
import farms_pylog as pylog


def exercise1(**kwargs):

    log_path = './logs/example_single/'  # path for logging the simulation data
    os.makedirs(log_path, exist_ok=True)

    all_pars = SimulationParameters(
        n_iterations=3001,
        controller="sine",
        log_path=log_path,
        compute_metrics=3,
        return_network=True,
        **kwargs
    )

    pylog.info("Running the simulation")
    controller = run_single(
        all_pars
    )

if __name__ == '__main__':
    exercise1(headless = False)

