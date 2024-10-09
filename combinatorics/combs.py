import json
import os
import shutil
import scipy
import argparse
from os import system

parser = argparse.ArgumentParser(
    description='Generate all possible constraint graphs for the given configuration and evaluates the Jacobian for a '
                'randomly generated synthetic scene.')
parser.add_argument('--config', type=str, help='The configuration of intrinsic parameters.')

if __name__ == "__main__":
    args = parser.parse_args()

    CONFIG_NAME = args.config
    NUM_THREADS = 1
    NUM_PARTITIONS = 1
    PARTITION_ID = 0

    # Kill all tmux sessions
    # system("tmux kill-server")

    # Read template config
    f = open("config.m2", "r")
    config_format = f.read()

    # Read config
    jsonf = open('configs.json')
    config = json.load(jsonf)['configs'][CONFIG_NAME]
    jsonf.close()

    params = {config['fxi'], config['fyi'], config['cx'], config['cy'], config['s']}
    params.discard('zer0')
    params.discard('one')
    nparams = len(params)
    npoints = 4 if nparams <= 1 else (5 if nparams <= 4 else 6)
    neqs = 2 * scipy.special.comb(npoints, 2)
    nunk = nparams + 3 * npoints - 1
    nrmv = neqs - nunk
    iters = scipy.special.comb(neqs, nrmv)

    # Define ranges
    num_elements = int(iters / NUM_PARTITIONS)
    start = num_elements * PARTITION_ID

    step = int(num_elements / NUM_THREADS)
    minrmv = start
    maxrmv = start + step

    for thread in range(int(NUM_THREADS)):
        add_limit = (0 if PARTITION_ID + 1 < NUM_PARTITIONS or maxrmv >= iters else 1)

        # Generate config.m2
        config_txt = config_format.format(
            fxi=config["fxi"],
            fyi=config["fyi"],
            cx=config["cx"],
            cy=config["cy"],
            s=config["s"],
            minrmv=int(minrmv),
            maxrmv=int(maxrmv if thread + 1 < NUM_THREADS else start + num_elements + add_limit)
        )

        # Write config.m2
        try:
            os.makedirs(f"results/{CONFIG_NAME}/")
        except OSError:
            pass
        f = open(f"results/{CONFIG_NAME}/config.m2", "w")
        f.write(config_txt)
        f.close()

        # Copy combs.m2 to this folder
        shutil.copyfile("combs.m2", f"results/{CONFIG_NAME}/combs.m2")

        # Run m2
        # system("tmux new-session -d -s combs-{}_{} 'cd results/{}/{}_{}; M2 combs.m2'".format(
        #    PARTITION_ID, thread, CONFIG_NAME, PARTITION_ID, thread))
        system(f"cd results/{CONFIG_NAME}/; M2 combs.m2")

        # Update for next iteration
        minrmv = minrmv + step
        maxrmv = maxrmv + step
