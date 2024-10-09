import argparse
import multiprocessing as mp
import os
import pathlib
import pickle
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Semaphore

import numpy as np
import pandas as pd

from lib.utils_lg import *

parser = argparse.ArgumentParser(description='Generate equivalence classes (vertex permutation only).')
parser.add_argument('--config', type=str, help='The configuration of intrinsic parameters.')
args = parser.parse_args()
CONFIG_NAME = args.config
NUM_POINTS = 5
if CONFIG_NAME == "00000":
    NUM_POINTS = 6


def parse(row):
    list = row['rmv'].replace('[', '').replace(']', '').split(';')
    (G, L) = constr2labels([eval(i) for i in list], NUM_POINTS, index=row["idx"])
    return row['idx'], G, L, row['is_singular']


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def spawn(blockId, return_dict, sema, min_idx, max_idx):
    print("Processing BLOCK_ID: {}, RANGE: ({}, {})".format(blockId, min_idx, max_idx))
    df = pd.read_csv(f'../combinatorics/results/{CONFIG_NAME}/output.csv')
    df = df.loc[df['idx'].isin(range(min_idx, max_idx + 1))]  # Inclusive range

    eq_list = []
    while df.shape[0] != 0:
        iso_list = []
        first = True

        for i, r in df.iterrows():
            if first:
                # print("EqC: {}, #: {}".format(i, len(eq_list)))
                first = False
                I1, G1, L1, S1 = parse(r)
                iso_list.append([I1, S1])
                df.drop(i, inplace=True)

            else:
                S2 = r['is_singular']
                if S1 != S2:
                    # Skip isomorphism check Jacobian rank is different
                    continue

                I2, G2, L2, S2 = parse(r)
                if is_isomorphic(G1, L1, G2, L2):
                    iso_list.append([I2, S2])
                    df.drop(i, inplace=True)

        # Add equivalence class to mapping
        eq_list.append(iso_list)

    return_dict[blockId] = eq_list
    sema.release()


def merge(chunk_id, return_dict, sema, flat_list):
    print("Processing CHUNK_ID: {}, len: {})".format(chunk_id, len(flat_list)))
    merged = []

    df = pd.read_csv(f'../combinatorics/results/{CONFIG_NAME}/output.csv')
    df = df.loc[df['idx'].isin(map(lambda x: x[0][0], flat_list))]  # Inclusive range
    mapping = {x[0][0]: ii for (ii, x) in enumerate(flat_list)}

    while df.shape[0] != 0:
        iso_list = []
        first = True

        for ii, r in df.iterrows():
            if first:
                first = False
                I1, G1, L1, S1 = parse(r)
                iso_list.extend(flat_list[mapping[ii]])
                df.drop(ii, inplace=True)

            else:
                S2 = r['is_singular']
                if S1 != S2:
                    # Skip isomorphism check Jacobian rank is different
                    continue

                I2, G2, L2, S2 = parse(r)
                if is_isomorphic(G1, L1, G2, L2):
                    iso_list.extend(flat_list[mapping[ii]])
                    df.drop(ii, inplace=True)

        merged.append(iso_list)

    print(f"Obtained CHUNK_ID: {chunk_id}, len: {len(merged)}")
    return_dict[chunk_id] = merged
    sema.release()


if __name__ == "__main__":
    # Performance
    NUM_WORKERS = 1
    NUM_BLOCKS = 1

    # Path
    BASE_PATH = f"{os.getcwd()}/results/{CONFIG_NAME}"
    CHECKPOINT = None

    print("Starting isomorphism.py...")
    print(f"NUM_WORKERS: {NUM_WORKERS}")
    print(f"NUM_BLOCKS: {NUM_BLOCKS}")

    # Increase maximum system open file limit
    os.system("ulimit -n 1024000")
    os.system("ulimit -Sn")

    # Create dirs
    pathlib.Path(f'{BASE_PATH}/pickle').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'{BASE_PATH}/eqs').mkdir(parents=True, exist_ok=True)

    # Read csv
    df = pd.read_csv(f'../combinatorics/results/{CONFIG_NAME}/output.csv')
    n_rows = df.shape[0]

    # ##################################################################################################################
    # Divide
    blocks = np.array_split(range(n_rows), NUM_BLOCKS)
    print("BLOCK_SIZE: {}".format(blocks[0][-1]))

    manager = mp.Manager()
    return_dict = manager.dict()
    q = Queue()
    sema = Semaphore(NUM_WORKERS)

    # Reload from checkpoint
    if CHECKPOINT:
        f = open(f"{BASE_PATH}/pickle/part_chkpt_{CHECKPOINT}.pkl", 'rb')
        chkpt = pickle.load(f)
        for key in chkpt.keys():
            return_dict[key] = chkpt[key]
        f.close()

    all_processes = []
    for blockId in range(NUM_BLOCKS):
        # Skip if already in checkpoint
        if blockId in return_dict.keys():
            if len(return_dict[blockId]) > 0:
                print(f"Skipping BLOCK_ID: {blockId}")
                continue

        # Write checkpoint
        f = open(f"{BASE_PATH}/pickle/part_chkpt_{blockId}.pkl", 'wb')
        chkpt = dict()
        for key in return_dict.keys():
            chkpt[key] = return_dict[key]
        pickle.dump(chkpt, f)
        f.close()

        # Start background process
        sema.acquire()
        p = Process(target=spawn, args=(blockId, return_dict, sema, blocks[blockId][0], blocks[blockId][-1]))
        all_processes.append(p)
        p.start()

    for p in all_processes:
        p.join()

    results = return_dict.values()

    # Checkpoint
    with open(f"{BASE_PATH}/pickle/chkpt.pkl", 'wb') as f:
        pickle.dump(results, f)

    # ##################################################################################################################
    # Conquer
    f = open(f"{BASE_PATH}/pickle/chkpt.pkl", 'rb')
    results = pickle.load(f)
    f.close()

    flat_list = [item for sublist in results for item in sublist]
    results = []

    # Multiprocessing
    NUM_STEPS = 8
    manager = mp.Manager()
    sema = Semaphore(NUM_WORKERS)

    for i in range(NUM_STEPS):
        print(f"Step {i}")
        if len(flat_list) <= pow(2, NUM_STEPS - i):
            break

        chunks = split_list(flat_list, pow(2, NUM_STEPS - i))

        # Build processes
        return_dict = manager.dict()
        all_processes = []
        for chunk_id, chunk in enumerate(chunks):
            # Start background process
            sema.acquire()
            p = Process(target=merge, args=(chunk_id, return_dict, sema, chunk))
            all_processes.append(p)
            p.start()

        # Wait for all processes
        for p in all_processes:
            p.join()

        flat_list = [item for sublist in return_dict.values() for item in sublist]

    return_dict = manager.dict()
    merge(-1, return_dict, sema, flat_list)
    merged = return_dict[-1]

    # Check that all configs are in the mapping
    assert sum(map(lambda x: len(x), merged)) == n_rows

    # ##################################################################################################################
    # Print results
    print(f"#EqCl: {len(merged)}")
    print(f"#EqCl NonSing: {sum(list(map(lambda x: not x[0][1], merged)))}")

    with open(f"{BASE_PATH}/pickle/eqcl.pkl", 'wb') as f:
        pickle.dump(results, f)

    # ##################################################################################################################
    # Export EqClass
    df = pd.read_csv(f'../combinatorics/results/{CONFIG_NAME}/output.csv')
    # Filter dataframe with only the first representative of the equivalence class
    eq_id = list(map(lambda x: x[0][0], merged))
    df = df[df.index.isin(eq_id)]
    df.to_csv(f"{BASE_PATH}/eqs/eqs.csv", index=False)
