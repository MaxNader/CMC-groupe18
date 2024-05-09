
from util.run_closed_loop import run_multiple
from simulation_parameters import SimulationParameters
import os
import numpy as np
import farms_pylog as pylog
from util.rw import load_object
import matplotlib.pyplot as plt
from plotting_common import plot_2d

def exercise8():

    pylog.info("Ex 8")
    pylog.info("Implement exercise 8")
    log_path = './logs/exercise8/'
    os.makedirs(log_path, exist_ok=True)

    sig_sim = 4
    gss_sim = 4
    sig_range = np.linspace(0, 30, sig_sim)
    gss_range = np.linspace(0, 10, gss_sim)
    tot_sim = sig_sim*gss_sim


    pars_list  = [SimulationParameters(
        n_iterations=3001,
        log_path=log_path,
        simulation_i=i*gss_sim+j,
        compute_metrics=3,
        noise_sigma = sig,
        w_stretch = ws,
        video_record=False,
        headless=True,
        print_metrics=False,
        return_network=True,
        method = 'noise'
    ) for i,sig in enumerate(sig_range) for j,ws in enumerate(gss_range)]
        
    networks = run_multiple(
        pars_list,num_process=8
    )
    fspeed= np.zeros([tot_sim, 3])
    for i,num in enumerate([i*gss_sim+j for i in range(gss_sim) for j in range(gss_sim)]):
        # load controller
        controller = load_object(log_path+"controller"+str(num))
        fspeed[i] = [
            controller.pars.noise_sigma,
            controller.pars.w_stretch,
            np.mean(controller.metrics["fspeed_PCA"])
        ]

    plt.figure('fspeed', figsize=[10, 10])
    plot_2d(
        fspeed,
        ['noise_sigma', 'w_stretch', 'fspeed_PCA'],
        cmap='nipy_spectral'
    )



if __name__ == '__main__':
    exercise8()
    plt.show()

