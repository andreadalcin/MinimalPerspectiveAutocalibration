import os
from pathlib import Path

import pandas as pd

from lib.drawer import draw
from lib.utils import *
import numpy as np

CONFIG_NAME = "00000"
NUM_POINTS = 5
if CONFIG_NAME == "00000":
    NUM_POINTS = 6

# Others
BASE_PATH = f"{os.getcwd()}/results/{CONFIG_NAME}"


def parse(row):
    list = row['rmv'].replace('[', '').replace(']', '').split(';')
    (G, L) = constr2labels([eval(i) for i in list], NUM_POINTS)
    return row['idx'], G, L, row['is_singular']


def parse_edges(r):
    return [eval(i) for i in r['rmv'].replace('[', '').replace(']', '').split(';')]


if __name__ == "__main__":
    Path(f'{BASE_PATH}/drawings/s').mkdir(parents=True, exist_ok=True)
    Path(f'{BASE_PATH}/drawings/ns').mkdir(parents=True, exist_ok=True)
    Path(f'{BASE_PATH}/stats/').mkdir(parents=True, exist_ok=True)

    kept = []

    df = pd.read_csv(f"{BASE_PATH}/eqs/eqs.csv")
    for i, r in df.iterrows():
        I1, G1, L1, S1 = parse(r)
        edges = parse_edges(r)
        image = draw(NUM_POINTS, edges)

        # Check minimum degrees for R+G separately (NOT RELEVANT)
        # adj = np.array(build_adj(NUM_POINTS, edges))
        # # Pair 1-2
        # R = np.logical_or(adj[:, :, 0], adj[:, :, 0].T)
        # deg_R = np.sum(R, axis=0)
        # min_deg_R = np.min(deg_R)
        # # Pair 1-3
        # G = np.logical_or(adj[:, :, 1], adj[:, :, 1].T)
        # deg_G = np.sum(G, axis=0)
        # min_deg_G = np.min(deg_G)
        #
        # # Every node should have degree >= 3, i.e., at least 3 outgoing edges
        # if min(min_deg_G, min_deg_R) >= 3:
        #     kept.append(I1)

        # Check minimum degrees for B (NOT RELEVANT)
        # adj = np.array(build_adj(NUM_POINTS, edges))
        # B = np.logical_or(adj[:, :, 0], adj[:, :, 1])
        # B = np.logical_or(B, B.T)
        # deg_B = np.sum(B, axis=0)
        # if np.min(deg_B) >= 3:
        #     kept.append(I1)
        # else:
        #     pass




    df = df[df.idx.isin(kept)]
    df.to_csv(f"{BASE_PATH}/stats/mindeg.csv", index=False)
