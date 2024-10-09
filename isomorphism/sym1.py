import argparse
import os
from pathlib import Path

import pandas as pd

from lib.utils import *

parser = argparse.ArgumentParser(description='Generate equivalence classes (view-pair permutation only).')
parser.add_argument('--config', type=str, help='The configuration of intrinsic parameters.')


def asym_constr2labels(constr_list, num_points):
    subsets = list(itertools.combinations((range(0, num_points)), 2))
    adj = list(map(lambda n: list(map(lambda m: [False, False], range(0, num_points))), range(0, num_points)))

    # Adjacency Tensor ( num_points, num_points, 2 )
    for constr in constr_list:
        subset = subsets[constr % len(subsets)]
        n1 = subset[0]  # 1st node
        n2 = subset[1]  # 2nd node

        if constr >= len(subsets):
            # Views 1-3
            adj[n1][n2][1] = True
            adj[n2][n1][1] = True
        else:
            # Views 1-2
            adj[n1][n2][0] = True
            adj[n2][n1][0] = True

    # Graph building
    G = build_labelled_graph(adj)

    # Vertex -> Label mapping
    L = []
    for i in range(num_points):
        tmp = []
        for j in range(num_points):
            if i != j:
                if adj[i][j][0] and adj[i][j][1]:
                    tmp.append("2")
                elif adj[i][j][0] or adj[i][j][1]:
                    tmp.append("1")

        tmp.sort()
        L.append("".join(tmp))

    return G, L


def parse(row, asym=False):
    list = row['rmv'].replace('[', '').replace(']', '').split(';')
    (G, L) = constr2labels([eval(i) for i in list], NUM_POINTS, asym=asym)
    return row['idx'], G, L, row['is_singular']


if __name__ == "__main__":
    args = parser.parse_args()

    # Combinatorics
    CONFIG_NAME = args.config
    NUM_POINTS = 5
    if CONFIG_NAME == "00000":
        NUM_POINTS = 6

    # Others
    BASE_PATH = f"{os.getcwd()}/results/{CONFIG_NAME}"

    Path(f'{BASE_PATH}/sym1/').mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(f"{BASE_PATH}/eqs/eqs.csv")
    n_rows = df.shape[0]

    merged = []
    while df.shape[0] != 0:
        iso_list = []
        first = True

        for i, r in df.iterrows():
            if first:
                print("EqC: {}, #: {}".format(i, len(merged)))
                first = False
                I1, G1, L1, S1 = parse(r)
                iso_list.append([I1, S1])
                df.drop(i, inplace=True)

            else:
                I2, G2, L2, S2 = parse(r, asym=True)
                if is_isomorphic(G1, L1, G2, L2):
                    iso_list.append([I2, S2])
                    df.drop(i, inplace=True)

        # Add equivalence class to mapping
        merged.append(iso_list)

    # Check that all configs are in the mapping
    assert sum(map(lambda x: len(x), merged)) == n_rows

    print(f"#EqCl: {len(merged)}")
    print(f"#EqCl NonSing: {sum(list(map(lambda x: not x[0][1], merged)))}")

    df = pd.read_csv(f"{BASE_PATH}/eqs/eqs.csv")
    # Filter dataframe with only the first representative of the equivalence class
    eq_id = list(map(lambda x: x[0][0], merged))
    df = df[df.idx.isin(eq_id)]
    df.to_csv(f"{BASE_PATH}/sym1/sym1.csv", index=False)
