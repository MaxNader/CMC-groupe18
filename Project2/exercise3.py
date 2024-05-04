
from util.run_open_loop import run_single
from simulation_parameters import SimulationParameters
import os
import farms_pylog as pylog
import matplotlib.pyplot as plt
from plotting_common import plot_left_right, plot_trajectory, plot_time_histories, plot_time_histories_multiple_windows

def exercise3():

    pylog.info("Ex 3")

    log_path = './logs/exercise3/'
    os.makedirs(log_path, exist_ok=True)

    pylog.info("Running the simulation")

    #default parameters
    all_pars = SimulationParameters(
        n_iterations=3001,
        controller="firing_rate",
        log_path=log_path,
        compute_metrics=3,
        return_network=True,
    )

    pylog.info("Running the simulation")
    controller = run_single(
        all_pars
    )

    pylog.info("Plotting the result")

    left_idx = controller.muscle_l
    right_idx = controller.muscle_r

    # example plot using plot_left_right
    plot_left_right(
        controller.times,
        controller.state,
        left_idx,
        right_idx,
        cm="green",
        offset=0.1)

    # example plot using plot_trajectory
    plt.figure("trajectory")
    plot_trajectory(controller)

    # example plot using plot_time_histories_multiple_windows
    plt.figure("joint positions")
    plot_time_histories_multiple_windows(
        controller.times,
        controller.joints_positions,
        offset=-0.4,
        colors="green",
        ylabel="joint positions",
        lw=1
    )

    # example plot using plot_time_histories
    plt.figure("link y-velocities")
    plot_time_histories(
        controller.times,
        controller.links_velocities[:, :, 1],
        offset=-0.,
        colors="green",
        ylabel="link y-velocities",
        lw=1
    )



if __name__ == '__main__':
    exercise3()


