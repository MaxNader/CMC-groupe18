

from util.run_closed_loop import run_single, run_multiple
from simulation_parameters import SimulationParameters
import os
import farms_pylog as pylog
import matplotlib.pyplot as plt
from plotting_common import plot_left_right, plot_trajectory, plot_time_histories, plot_time_histories_multiple_windows
import numpy as np


def exercise6(**kwargs):

    pylog.info("Ex 6")

    log_path = './logs/exercise6/'
    os.makedirs(log_path, exist_ok=True)

    gss_sim = 10
  
    gss_range = np.linspace(0, 15, gss_sim)
 
    tot_sim = gss_sim

    lat_speeds = np.zeros(tot_sim)
    curvature = np.zeros(tot_sim)


    pars_list  = [SimulationParameters(
        n_iterations=3001,
        log_path=log_path,
        simulation_i=i,
        compute_metrics=3,
        w_stretch= gss,
        print_metrics=False,
        video_record=False,
        headless=True,
        return_network=True,
    ) for i,gss in enumerate(gss_range)]
        
    networks = run_multiple(
        pars_list,num_process=8
    )

    freqs = [net.metrics["frequency"] for net in networks]
    wavefreqs = [net.metrics["wavefrequency"] for net in networks]
    fspeeds = [net.metrics["fspeed_PCA"] for net in networks]
    
    plt.figure('frequency')
    plt.plot(gss_range, freqs)
    plt.xlabel('gss')
    plt.ylabel('frequency')

    plt.figure('wave_frequency')
    plt.plot(gss_range, wavefreqs)
    plt.xlabel('gss')
    plt.ylabel('wave_frequency')

    plt.figure('fspeed')
    plt.plot(gss_range, fspeeds)
    plt.xlabel('gss')
    plt.ylabel('fspeed')


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
    
    # Sensory neurons activities
    plt.figure('SS_activities_single')
    plot_left_right(
        controller.times,
        controller.state,
        controller.L_s,
        controller.R_s,
        cm="blue",
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
    exercise6(headless=False)
    plt.show()

