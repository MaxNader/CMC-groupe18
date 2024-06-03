

from simulation_parameters import SimulationParameters
from util.run_closed_loop import run_multiple
import numpy as np
import farms_pylog as pylog
import os
from util.run_closed_loop import run_single
import matplotlib.pyplot as plt
from plotting_common import plot_left_right, plot_trajectory, plot_time_histories, plot_time_histories_multiple_windows
import farms_pylog as pylog
from metrics import compute_curvature
from util.rw import load_object
from plotting_common import plot_2d

def exercise7():

    pylog.info("Ex 7")
    
    log_path = './logs/exercise7/'
    os.makedirs(log_path, exist_ok=True)
    I = 30
    w_stretch_list= np.linspace(0, 15, 4)
    Idiff_list = np.linspace(0, 2, 4)
    n_sim = 4
    pars_list = [
        SimulationParameters(
            n_iterations=3001,
            log_path=log_path,
            simulation_i=i*n_sim+j,
            video_record=False,
            compute_metrics=3,
            w_stretch=gss,
            return_network=True,
            Idiff = Id,
            n_desc = 8,
            print_metrics=False,
            headless=True,
            I=I
    ) for i, gss in enumerate(w_stretch_list) for j, Id in enumerate(Idiff_list)]
    networks = run_multiple(pars_list, num_process=6)

    run_multiple(
        pars_list,num_process=8
    )
    curvatures = np.zeros([len(w_stretch_list)* len(Idiff_list),3])
    lat_speeds = np.zeros([len(w_stretch_list)* len(Idiff_list),3])
    fspeeds = np.zeros([len(w_stretch_list)* len(Idiff_list),3])
    ptccs = np.zeros([len(w_stretch_list)* len(Idiff_list),3])
    freqs = np.zeros([len(w_stretch_list)* len(Idiff_list),3])
    wavefreqs = np.zeros([len(w_stretch_list)* len(Idiff_list),3])
    for i,num in enumerate([i*n_sim+j for i in range(n_sim) for j in range(n_sim)]):
        # load controller
        controller = load_object(log_path+"controller"+str(num))

        ptccs[i] = [
            controller.pars.Idiff,
            controller.pars.w_stretch,
            np.mean(controller.metrics["ptcc"])
        ]
        fspeeds[i] =  [
            controller.pars.Idiff,
            controller.pars.w_stretch,
            np.mean(controller.metrics["fspeed_PCA"])
        ]
        lat_speeds[i] =  [
            controller.pars.Idiff,
            controller.pars.w_stretch,
            np.mean(controller.metrics["lspeed_PCA"])
        ]
        curvatures[i] =  [
            controller.pars.Idiff,
            controller.pars.w_stretch,
            np.mean(controller.metrics["curvature"])
        ]

        freqs[i] =  [
            controller.pars.Idiff,
            controller.pars.w_stretch,
            np.mean(controller.metrics["frequency"])
        ]
        wavefreqs[i] =  [   
            controller.pars.Idiff,
            controller.pars.w_stretch,
            np.mean(controller.metrics["wavefrequency"])
        ]

    
    plt.figure('curvature{}'.format(I), figsize=[10, 10])
    plot_2d(
        curvatures,
        [ 'Idiff','w_stretch', 'curvature'],
        cmap='nipy_spectral'
    )
    plt.figure('lat_speed{}'.format(I), figsize=[10, 10])
    plot_2d(
        lat_speeds,
        [ 'Idiff', 'w_stretch','lspeed_PCA'],
        cmap='nipy_spectral'
    )
    plt.figure('fspeed{}'.format(I), figsize=[10, 10])
    plot_2d(
        fspeeds,
        [ 'Idiff', 'w_stretch','fspeed_PCA'],
        cmap='nipy_spectral'
    )
    plt.figure('oscillation stability{}'.format(I), figsize=[10, 10])
    plot_2d(
        ptccs,
        [ 'Idiff', 'w_stretch','PTCC'],
        cmap='nipy_spectral'
    )


    plt.figure('frequency{}'.format(I), figsize=[10, 10])
    plot_2d(
        freqs,
        ['Idiff', 'w_stretch', 'frequency'],
        cmap='nipy_spectral'
    )
    plt.figure('wave_frequency{}'.format(I), figsize=[10, 10])
    plot_2d(
        wavefreqs,
        ['Idiff', 'w_stretch', 'wavefrequency'],
        cmap='nipy_spectral'
    )

    

if __name__ == '__main__':
    exercise7()
    plt.show()

