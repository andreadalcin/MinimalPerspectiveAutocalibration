import os

import numpy as np
import pandas as pd

from lib.utils import *
from lib.rigidity import rigidity

CONFIG_NAME = "00000"
NUM_POINTS = 6
# Others
DF_PATH = f"{os.getcwd()}/results/{CONFIG_NAME}/eqs/eqs.csv"


def parse(row):
    list = row['rmv'].replace('[', '').replace(']', '').split(';')
    (G, L) = constr2labels([eval(i) for i in list], NUM_POINTS)
    return row['idx'], G, L, row['is_singular']


def parse_edges(r):
    return [eval(i) for i in r['rmv'].replace('[', '').replace(']', '').split(';')]


# Counting argument on the 6-point graph
def hyp0(edges):
    verify = False
    A = np.array(build_adj(NUM_POINTS, edges))
    n_points = A.shape[0]
    assert n_points == 6

    missR = 0
    missG = 0
    for i1 in range(n_points - 1):
        for i2 in range(i1 + 1, n_points):
            if not A[i1][i2][0] and not A[i1][i2][1]:
                missR += 1
                missG += 1
            else:
                if not A[i1][i2][0]:
                    missR += 1
                if not A[i1][i2][1]:
                    missG += 1

    # Either graph (1-2 or 1-3) is under-constrained
    if missR > 5:
        verify = True
        rr = np.linalg.matrix_rank(rigidity(A[:, :, 0]))
        print(f"{verify}: {rr}")

    if missG > 5:
        verify = True
        rr = np.linalg.matrix_rank(rigidity(A[:, :, 1]))
        print(f"{verify}: {rr}")

    if not verify:
        rr = np.linalg.matrix_rank(rigidity(A[:, :, 0]))
        rg = np.linalg.matrix_rank(rigidity(A[:, :, 1]))
        print(f"{verify}: {rr}, {rg}")

    return verify


# Counting argument on all possible 5-point sub-graphs
def hyp1(edges):
    verify = False
    A = np.array(build_adj(NUM_POINTS, edges))

    # Check all 5-point sub-graphs
    for node in range(A.shape[0]):
        S = np.delete(np.delete(A, node, axis=0), node, axis=1)
        n_points = S.shape[0]
        assert n_points == 5
        missR = 0
        missG = 0
        for i1 in range(n_points - 1):
            for i2 in range(i1 + 1, n_points):
                if not S[i1][i2][0] and not S[i1][i2][1]:
                    missR += 1
                    missG += 1
                else:
                    if not S[i1][i2][0]:
                        missR += 1
                    if not S[i1][i2][1]:
                        missG += 1

        # Either graph (1-2 or 1-3) is over-constrained
        if missR == 0:
            verify = True

        if missG == 0:
            verify = True

        rr = np.linalg.matrix_rank(S[:, :, 0])
        print(f"{verify}: {rr}")
        rr = np.linalg.matrix_rank(S[:, :, 1])
        print(f"{verify}: {rr}")

    return verify


if __name__ == "__main__":
    df = pd.read_csv(DF_PATH)

    print("Hello! This script verifies that a configuration satisfies either rule if and only if it is results in a "
          "singular Jacobian!")

    # Verify: 6-point graph rule
    ok = []  # IDs of configurations that are identified as singular
    ko1 = []  # IDs of configurations not identified as singular

    for i, r in df.iterrows():
        I1, G1, L1, S1 = parse(r)
        edges = parse_edges(r)
        verify = hyp0(edges)
        if verify:
            assert S1  # If the configuration satisfies the rule, then it must be singular
            ok.append(I1)
        if not verify and S1:
            print("KO")
            ko1.append(I1)

    print("Partial results after hyp0:")
    print(f"OK: {len(ok)}")
    print(f"KO: {len(ko1)}")

    # Verify: 5-point sub-graph rule
    ko2 = []

    for i, r in df.iterrows():
        I1, G1, L1, S1 = parse(r)
        if I1 in ok:
            # ID already identified as singular
            continue

        edges = parse_edges(r)
        verify = hyp1(edges)
        if verify:
            assert S1  # If the configuration satisfies the rule, then it must be singular
            ok.append(I1)
        if not verify and S1:
            ko2.append(I1)

    print("Results after hyp1:")
    print(f"OK: {len(ok)}")
    print(f"KO: {len(ko2)}")

    if len(ko2) == 0:
        print("Success!")
