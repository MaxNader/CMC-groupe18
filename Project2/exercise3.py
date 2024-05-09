
from util.run_closed_loop import run_single
from simulation_parameters import SimulationParameters
import os
import farms_pylog as pylog
import matplotlib.pyplot as plt
from plotting_common import plot_left_right, plot_trajectory, plot_time_histories, plot_time_histories_multiple_windows

def exercise3(**kwargs):

    pylog.info("Ex 3")

    log_path = './logs/exercise3/'
    os.makedirs(log_path, exist_ok=True)

    all_pars = SimulationParameters(
        n_iterations=5001,
        log_path=log_path,
        compute_metrics=3,
        return_network=True,
        **kwargs
    )

    pylog.info("Running the simulation")
    controller = run_single(
        all_pars
    )

    pylog.info("Plotting the result")

    left_idx = controller.muscle_l
    right_idx = controller.muscle_r

    # example plot using plot_left_right
    plt.figure('muscle_activities_single')
    plot_left_right(
        controller.times,
        controller.state,
        left_idx,
        right_idx,
        cm="green",
        offset=0.1)
    
    # CPG firing rates
    plt.figure('CPG_firing_rates_single')
    plot_left_right(
        controller.times,
        controller.state,
        controller.L_v,
        controller.R_v,
        cm="green",
        offset=0.1)
    
    # CPG adaptations
    plt.figure('CPG_adaptations_single')
    plot_left_right(
        controller.times,
        controller.state,
        controller.L_a,
        controller.R_a,
        cm="green",
        offset=0.1)



    # example plot using plot_time_histories_multiple_windows
    plt.figure("joint positions_single")
    plot_time_histories_multiple_windows(
        controller.times,
        controller.joints_positions,
        offset=-0.4,
        colors="green",
        ylabel="joint positions",
        lw=1
    )




if __name__ == '__main__':
    exercise3(headless=False)
    plt.show()


