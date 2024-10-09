import pandas as pd
from utils import *


def parse(row):
    list = row['rmv'].replace('[', '').replace(']', '').split(';')
    (G, L) = constr2labels([eval(i) for i in list], NUM_POINTS)
    return row['idx'], G, L, row['is_singular']


def spawn(df, min_idx, max_idx):
    df = df.loc[df['id'].isin(range(min_idx, max_idx))]
    while df.shape[0] != 0:
        iso_list = []
        first = True

        for i, r in df.iterrows():
            if first:
                print("EqC: {}".format(i))
                first = False
                I1, G1, L1, S1 = parse(r)
                iso_list.append([I1, S1])

                df.drop(i, inplace=True)
            else:
                S2 = r['is_singular']
                if S1 != S2:
                    # Skip isomorphism check Jacobian rank is different
                    # print("Skipping..")
                    continue

                I2, G2, L2, S2 = parse(r)
                if is_isomorphic(G1, L1, G2, L2):
                    print("[{}:{}]: ISO_OK".format(I1, I2))
                    iso_list.append([I2, S2])
                    # Drop
                    df.drop(i, inplace=True)
                    # print("Dropping {}...".format(i))

        # Add equivalence class to mapping
        mapping.append(iso_list)


if __name__ == "__main__":
    # NUM_POINTS = 5
    NUM_POINTS = 6
    CONFIG_NAME = "00000"

    df = pd.read_csv('../combinatorics/results/{}/0_0/output.csv'.format(CONFIG_NAME))
    n_rows = df.shape[0]

    mapping = []

    while df.shape[0] != 0:
        iso_list = []
        first = True

        for i, r in df.iterrows():
            if first:
                print("EqC: {}".format(i))
                first = False
                I1, G1, L1, S1 = parse(r)
                iso_list.append([I1, S1])

                df.drop(i, inplace=True)
            else:
                S2 = r['is_singular']
                if S1 != S2:
                    # Skip isomorphism check Jacobian rank is different
                    # print("Skipping..")
                    continue

                I2, G2, L2, S2 = parse(r)
                if is_isomorphic(G1, L1, G2, L2):
                    print("[{}:{}]: ISO_OK".format(I1, I2))
                    iso_list.append([I2, S2])
                    # Drop
                    df.drop(i, inplace=True)
                    # print("Dropping {}...".format(i))

        # Add equivalence class to mapping
        mapping.append(iso_list)

    # Check that all configs are in the mapping
    assert sum(map(lambda x: len(x), mapping)) == n_rows

    # Print results
    print("#EqCl: {}".format(len(mapping)))
    print("#EqCl NonSing: {}".format(sum(list(map(lambda x: not x[0][1], mapping)))))
