from util.run_closed_loop import run_multiple
from simulation_parameters import SimulationParameters
from util.run_closed_loop import run_single
import os
import numpy as np
import farms_pylog as pylog
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

def exercise_multiple():
    log_path = './logs/example_multiple/'
    os.makedirs(log_path, exist_ok=True)

    nsim = 4
    pylog.info(
        "Running multiple simulations in parallel from a list of SimulationParameters")
    all_results = []
    best_fspeed = 0
    best_freq = 0
    for freq in range(1, 6):
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
                return_network=True
            )
            for i, amp in enumerate(np.linspace(0.8, 1, nsim))
            for j, wavefrequency in enumerate(np.linspace(0.6, 0.8, nsim))
        ]

        networks = run_multiple(pars_list, num_process=6)
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