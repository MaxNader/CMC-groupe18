
from util.run_closed_loop import run_multiple
from util.run_closed_loop import run_single
from simulation_parameters import SimulationParameters
import os
import numpy as np
import farms_pylog as pylog


def exercise2():

    pylog.info("Ex 2")

    log_path = './logs/exercise2/'
    os.makedirs(log_path, exist_ok=True)
    nsim = 4
    pylog.info(
        "Running multiple simulations in parallel from a list of SimulationParameters")
    all_results = []
    
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
            for i, lam in enumerate([0,25,50,100])
        ]
    networks = run_multiple(pars_list, num_process=6)
    metrics_dictlist = [net.metrics for net in networks]

    sorted_metrics_list = sorted(metrics_dictlist, key=lambda x: x['fspeed_PCA'], reverse=True)

    dict_with_max_value = sorted_metrics_list[0]
    best_lam = dict_with_max_value['lam']

    fspeed = dict_with_max_value['fspeed_PCA']

    all_results.append((best_lam, dict_with_max_value['fspeed_PCA']))

    if fspeed > best_fspeed:
            best_fspeed = fspeed


    for result in all_results:
        best_lam, fspeed = result
        print('Best lambda is: lambda =', best_lam, ', fspeed =', fspeed)

  
    print('RUNNING FASTEST ZEBRAFISH NOW')
    pars = SimulationParameters(
        n_iterations=3001,
        controller="sine",
        log_path=log_path,
        compute_metrics=3,
        return_network=True,
        amp = 1.2/2,
        freq = 5,
        wavefrequency = 0.665,
        headless = False,
        activation_func = [True,best_lam,0.5]
    )
    run_single(pars)

if __name__ == '__main__':
    exercise2()

