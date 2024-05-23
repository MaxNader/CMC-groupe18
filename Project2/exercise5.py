

from simulation_parameters import SimulationParameters
from util.run_closed_loop import run_multiple
import numpy as np
import farms_pylog as pylog
import os
from util.run_closed_loop import run_single
from plotting_common import plot_2d
import matplotlib.pyplot as plt
import os
from plotting_common import plot_left_right, plot_trajectory, plot_time_histories, plot_time_histories_multiple_windows
import farms_pylog as pylog
from metrics import compute_curvature
def exercise5():

    pylog.info("Ex 5")
    
    log_path = './logs/exercise5/'
    os.makedirs(log_path, exist_ok=True)

    nsim=1
       

    Idiff_list= np.linspace(0, 4, 4)
    pars_list = [
        SimulationParameters(
            simulation_i=nsim,
            n_iterations=3001,
            log_path=log_path,
            video_record=False,
            compute_metrics=3,
            Idiff=Id,
            return_network=True,
            stretch = False,
    )
    for i, Id in enumerate(Idiff_list)]
    networks = run_multiple(pars_list, num_process=6)
    curvatures_list = [net.metrics["curvature"] for net in networks]
    lat_speed_list = [net.metrics["lspeed_PCA"] for net in networks]
    plt.figure('Trajectories')
    for i, network in enumerate(networks):
        curvature=curvatures_list[i]
        #print(f"Idiff = {Idiff_list[i]}")
        #print(f"Curvature: {curvature}\n")

        # Plot trajectory for each Idiff
        plt.subplot(int(np.ceil(np.sqrt(len(networks)))),int(np.ceil(np.sqrt(len(networks)))), i + 1, aspect='equal', adjustable='box', autoscale_on=True)
        plot_trajectory(network)
        #plt.title(f"Trajectory for Idiff = {Idiff_list[i]}")
    plt.figure('Traj2')
    for i,ind in enumerate([0,1]):
        plt.subplot(1,2, i + 1)
        plot_trajectory(networks[ind])
    plt.figure('Muscle Activities')
    
    left_idx = networks[0].muscle_l
    right_idx = networks[0].muscle_r
        # Plot trajectory for each Idiff
    plt.figure('Muscle Activities I=0')
    plot_left_right(
        networks[0].times,
        networks[0].state,
        left_idx,
        right_idx,
        cm="green",
        offset=0.1)
    plt.figure('Muscle Activities I=1')
    plot_left_right(
        networks[1].times,
        networks[1].state,
        left_idx,
        right_idx,
        cm="green",
        offset=0.1)
    plt.figure('CPG Firing Rates I=0')
    plot_left_right(
        networks[0].times,
        networks[0].state,
        networks[0].L_v,
        networks[0].R_v,
        cm="green",
        offset=0.1)
    plt.figure('CPG Firing Rates I=1')

    plot_left_right(
        networks[1].times,
        networks[1].state,
        networks[1].L_v,
        networks[1].R_v,
        cm="green",
        offset=0.1)
    plt.figure('CPG Adaptations I=0')
    plot_left_right(
        networks[0].times,
        networks[0].state,
        networks[0].L_a,
        networks[0].R_a,
        cm="green",
        offset=0.1)
    plt.figure('CPG Adaptations I=1')
    plot_left_right(
        networks[1].times,
        networks[1].state,
        networks[1].L_a,
        networks[1].R_a,
        cm="green",
        offset=0.1)
    

    plt.figure('Curvature')
    plt.plot(Idiff_list, curvatures_list)
    plt.xlabel('Idiff')
    plt.ylabel('Curvature')

    plt.figure('Lat Speed')
    plt.plot(Idiff_list, lat_speed_list)
    plt.xlabel('Idiff')
    plt.ylabel('Lat Speed')

    
        


if __name__ == '__main__':
    exercise5()
    plt.show()



