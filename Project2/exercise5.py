

from simulation_parameters import SimulationParameters
from util.run_closed_loop import run_multiple
import numpy as np
import farms_pylog as pylog
import os
from util.run_closed_loop import run_single
from simulation_parameters import SimulationParameters
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
       

    Idiff_list= np.linspace(0, 4, 12)
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

    for i, network in enumerate(networks):
        curvature=curvatures_list[i]
        print(f"Idiff = {Idiff_list[i]}")
        print(f"Curvature: {curvature}\n")
    
        # Plot trajectory for each Idiff
        plt.subplot(6,2, i + 1)
        plot_trajectory(network)
        plt.title(f"Trajectory for Idiff = {Idiff_list[i]}")
    
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



