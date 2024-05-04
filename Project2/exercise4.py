
from util.rw import load_object
from simulation_parameters import SimulationParameters
from util.run_open_loop import run_multiple
from plotting_common import plot_2d
import matplotlib.pyplot as plt
import numpy as np
import farms_pylog as pylog
import os


def exercise4():

    pylog.info("Ex 4")


    log_path = './logs/exercise4/'
    os.makedirs(log_path, exist_ok=True)
    n_simulations = 5
    I_sim = 10
    n_sim = 10
    I_range = np.arange(0, 30, I_sim)
    n_range = np.arange(0, 10, n_sim)
    tot_sim = I_sim*n_sim
    ptccs = np.zeros([tot_sim, 3])
    freqs = np.zeros([tot_sim, 3])
    wavefreqs = np.zeros([tot_sim, 3])

    pars_list  = [SimulationParameters(
        n_iterations=3001,
        log_path=log_path,
        simulation_i=i*n_simulations+j,
        compute_metrics=3,
        I=I,
        n_desc = n,
        video_record=False,
        headless=True,
        print_metrics=False
    ) for i,n in enumerate(n_range) for j,I in enumerate(I_range)]
        
    run_multiple(
        pars_list,num_process=8
    )
    
    for i,num in enumerate([i*n_simulations+j for i in range(len(np.arange(0,10,2))) for j in range(len(I_range))]):
        # load controller
        controller = load_object(log_path+"controller"+str(num))
        ptccs[i] = [
            controller.pars.I,
            controller.pars.n_desc,
            np.mean(controller.metrics["ptcc"])
        ]
        freqs[i] =  [
            controller.pars.I,
            controller.pars.n_desc,
            np.mean(controller.metrics["frequency"])
        ]
        wavefreqs[i] =  [
            controller.pars.I,
            controller.pars.n_desc,
            np.mean(controller.metrics["wavefrequency"])
        ]

    plt.figure('oscillation stability', figsize=[10, 10])
    plot_2d(
        ptccs,
        ['I', 'n_desc', 'PTCC'],
        cmap='nipy_spectral'
    )
    plt.figure('frequency', figsize=[10, 10])
    plot_2d(
        freqs,
        ['I', 'n_desc', 'frequency'],
        cmap='nipy_spectral'
    )
    plt.figure('wave frequency', figsize=[10, 10])
    plot_2d(
        wavefreqs,
        ['I', 'n_desc', 'wavefrequency'],
        cmap='nipy_spectral'
    )



if __name__ == '__main__':
    exercise4()
    plt.show()

