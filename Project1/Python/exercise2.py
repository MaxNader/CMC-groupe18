
from util.run_closed_loop import run_multiple
from util.run_closed_loop import run_single
from simulation_parameters import SimulationParameters
import matplotlib.pyplot as plt
import os
import numpy as np
import farms_pylog as pylog
from plotting_common import plot_left_right, plot_trajectory, plot_time_histories, plot_time_histories_multiple_windows


def exercise2():

    pylog.info("Ex 2")

    log_path = './logs/exercise2/'
    os.makedirs(log_path, exist_ok=True)
    nsim = 4
    pylog.info(
        "Running multiple simulations in parallel from a list of SimulationParameters")
    
    lam_list = np.linspace(0,30,50)
    pars_list = [
            SimulationParameters(
                simulation_i=i*nsim,
                n_iterations=3001,
                log_path=log_path,
                video_record=False,
                compute_metrics=3,
                freq=5,  
                amp=1.2/2,
                wavefrequency=0.665,
                headless=True,
                print_metrics=False,
                return_network=True,
                activation_func = [True,lam,0.5]
            )
            for i, lam in enumerate(lam_list)
        ]
    networks = run_multiple(pars_list, num_process=6)
    speeds_list = [net.metrics["fspeed_PCA"] for net in networks]

    max_lambda = max(zip(speeds_list, lam_list))
    print("the best lambda is : ", max_lambda[1], " for the highest speed : ", max(speeds_list))

    all_pars = SimulationParameters(
        n_iterations=3001,
        controller="sine",
        log_path=log_path,
        compute_metrics=3,
        return_network=True,
        amp = 1.2/2,
        freq = 5,
        wavefrequency = 0.665,
        activation_func = [True,max_lambda[1],0.5]
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


    plt.figure("speed VS lambda")
    plt.plot(lam_list,speeds_list)




if __name__ == '__main__':
    exercise2()
    plt.show()

