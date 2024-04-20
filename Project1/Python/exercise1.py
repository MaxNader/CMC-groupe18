from util.run_closed_loop import run_multiple
from simulation_parameters import SimulationParameters
from util.run_closed_loop import run_single
import plot_results
import os
import numpy as np
import matplotlib.pyplot as plt
import farms_pylog as pylog
from util.rw import load_object
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

def exercise_multiple():
    log_path = './logs/example_multiple/'
    os.makedirs(log_path, exist_ok=True)

    nsim = 5
    pylog.info(
        "Running multiple simulations in parallel from a list of SimulationParameters")
    all_results = []
    best_fspeed = 0
    best_freq = 0
    freqs = [1]
    for freq in freqs:
        pars_list = [
            SimulationParameters(
                simulation_i=i*nsim+j,
                n_iterations=3001,
                log_path=log_path,
                video_record=False,
                compute_metrics=3,
                freq=freq,  
                amp=amp/2,
                wavefrequency=wavefrequency,
                headless=True,
                print_metrics=False,
                return_network=True,
                activation_func = [False,50,0.5]
            )
            for i, amp in enumerate(np.linspace(0.01, 2, nsim))
            for j, wavefrequency in enumerate(np.linspace(0.01, 2, nsim))
        ]

        networks = run_multiple(pars_list, num_process=8)
        metrics_dictlist = [net.metrics for net in networks]

        sorted_metrics_list = sorted(
            metrics_dictlist, key=lambda x: x['fspeed_PCA'], reverse=True)

        dict_with_max_value = sorted_metrics_list[0]  
        best_amp = dict_with_max_value['amp']
        best_wavefrequency = dict_with_max_value['wavefrequency']
        fspeed = dict_with_max_value['fspeed_PCA']

        all_results.append((freq, best_amp, best_wavefrequency, dict_with_max_value['fspeed_PCA']))

        if fspeed > best_fspeed:
            best_fspeed = fspeed
            best_freq = freq

    for result in all_results:
        freq, best_amp, best_wavefrequency, fspeed = result
        print('For frequency =', freq, 'Hz, best params are: amp =', best_amp, ', wave frequency =', best_wavefrequency, ', fspeed =', fspeed)
    

    fspeeds = np.zeros([nsim**2, 3])

    for i in range(nsim**2):
        # Charger le contrôleur depuis le fichier
        controller = load_object(log_path + "controller" + str(i))
        
        # Extraire les valeurs d'amp, wavefrequency et fspeed_PCA
        fspeeds[i] = [
            controller.pars.amp,
            controller.pars.wavefrequency,
            controller.metrics["fspeed_PCA"]  # Correction de fspeed_cycle à fspeed_PCA
        ]


    plt.figure('exercise_multiple', figsize=[10, 10])
    plot_results.plot_2d(
    fspeeds,
    ['amp', 'wavefrequency', 'Forward Speed [m/s]'],
    cmap='nipy_spectral'
    )
    plt.show()

    print("Best frequency with the highest fspeed:", best_freq, "Hz")
    print('RUNNING FASTEST ZEBRAFISH NOW')
    pars = SimulationParameters(
        n_iterations=3001,
        controller="sine",
        log_path=log_path,
        compute_metrics=3,
        return_network=True,
        amp = best_amp/2,
        freq = best_freq,
        wavefrequency = best_wavefrequency,
        headless = False
    )
    run_single(pars)


if __name__ == '__main__':
    exercise_multiple()