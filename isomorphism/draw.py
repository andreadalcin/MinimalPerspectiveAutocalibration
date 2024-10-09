import os
from pathlib import Path

import pandas as pd

from lib.drawer import draw
from lib.utils import *

CONFIG_NAME = "00001"
SYMMETRY = "sym1"
NUM_POINTS = 5
if CONFIG_NAME == "00000":
    NUM_POINTS = 6

# Others
if SYMMETRY:
    BASE_PATH = f"{os.getcwd()}/results/{CONFIG_NAME}/{SYMMETRY}"
else:
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

    if SYMMETRY:
        df = pd.read_csv(f"{BASE_PATH}/{SYMMETRY}.csv")
    else:
        df = pd.read_csv(f"{BASE_PATH}/eqs/eqs.csv")

    for i, r in df.iterrows():
        I1, G1, L1, S1 = parse(r)
        edges = parse_edges(r)
        image = draw(NUM_POINTS, edges)
        if S1:
            image.write_file(f"{BASE_PATH}/drawings/s/{I1}.png")
        else:
            image.write_file(f"{BASE_PATH}/drawings/ns/{I1}.png")

        adj = build_adj(NUM_POINTS, edges)
        missing_r = 0
        missing_g = 0
        # missing_b = 0
        for i1 in range(NUM_POINTS - 1):
            for i2 in range(i1 + 1, NUM_POINTS):
                if not adj[i1][i2][0] and not adj[i1][i2][1]:
                    missing_r += 1
                    missing_g += 1
                else:
                    if not adj[i1][i2][0]:
                        missing_r += 1
                    if not adj[i1][i2][1]:
                        missing_g += 1

        if S1:
            print(f"[{I1}, s={S1}]:\tR: {missing_r}, G: {missing_g}")