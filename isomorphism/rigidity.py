import os
from pathlib import Path

import pandas as pd
import scipy.special

from lib.drawer import draw
from lib.utils import *
import numpy as np

CONFIG_NAME = "00011"
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


def rigidity(A):
    assert A.shape[0] == A.shape[1]
    num_points = A.shape[0]
    A = np.logical_or(A, A.T)
    pnt = np.random.rand(num_points, 3)
    edges = list(itertools.combinations((range(num_points)), 2))

    n = num_points
    m = len(edges)
    d = 3

    R = np.zeros(shape=(m, d * n))
    for ii, (u, v) in enumerate(edges):
        if A[u][v]:
            R[ii, u * 3:u * 3 + 3] = pnt[u, :] - pnt[v, :]
            R[ii, v * 3:v * 3 + 3] = pnt[v, :] - pnt[u, :]

    return R


def chk_sub(A):
    d = 3
    probably_singular = True

    for n in range(NUM_POINTS):
        As = np.delete(np.delete(A, n, axis=0), n, axis=1)
        assert As.shape[0] == NUM_POINTS - 1 and As.shape[1] == NUM_POINTS - 1

        RG = rigidity(As[:, :, 0])
        RB = rigidity(As[:, :, 1])
        expected_rank = 3 * (NUM_POINTS - 1) - scipy.special.binom(d + 1, 2)

        if np.linalg.matrix_rank(RG) >= expected_rank and np.linalg.matrix_rank(RB) >= expected_rank:
            probably_singular = False

    return probably_singular



if __name__ == "__main__":
    kept = []

    df = pd.read_csv(f"{BASE_PATH}/eqs/eqs.csv")
    for i, r in df.iterrows():
        I1, G1, L1, S1 = parse(r)
        edges = parse_edges(r)

        A = np.array(build_adj(NUM_POINTS, edges))
        if chk_sub(A):
            assert S1


        # RR = rigidity(A[:, :, 0])
        # RG = rigidity(A[:, :, 1])
        #
        # rr = np.linalg.matrix_rank(RR)
        # rg = np.linalg.matrix_rank(RG)
        #
        # d = 3
        # expected_rank = 3 * NUM_POINTS - scipy.special.binom(d + 1, 2)
        #
        # # print(f"Singular: {S1}")
        # # print(f"Expected rank: {expected_rank}")
        # # print(rr)
        # # print(rg)
        #
        # if rr < expected_rank or rg < expected_rank:
        #     assert S1
