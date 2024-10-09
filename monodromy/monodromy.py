import argparse
import json
from pathlib import Path
import shutil

import pandas as pd

parser = argparse.ArgumentParser(
    description='Runs monodromy for the chosen configuration on all equivalence classes.')
parser.add_argument('--config', type=str, help='The calibration configuration.')


def gen_eqc_list(args):
    eqc_list = []

    # Load csv
    df = pd.read_csv(f"isomorphism/results/{args.config}/sym1/sym1.csv")
    for i, r in df.iterrows():
        if not r['is_singular']:
            eqc = r['rmv'].replace('[', '').replace(']', '').split(';')
            eqc_list.append(eqc)

    return eqc_list


def gen_config(args, eqc_list):
    # Read template config
    f = open("monodromy/m2/skew-2/config.m2", "r")
    config_f = f.read()

    # Read JSON config
    json_file = open('combinatorics/configs.json')
    json_config = json.load(json_file)['configs'][args.config]
    json_file.close()

    # params = {
    #     json_config['fxi'],
    #     json_config['fyi'],
    #     json_config['cx'],
    #     json_config['cy'],
    #     json_config['s']
    # }
    # params.discard('zer0')
    # params.discard('one')

    eqc_str = ""
    for eqc in eqc_list:
        if len(eqc_str) > 0:
            eqc_str += ","
        eqc_str += "{" + ",".join(eqc) + "}"

    text = config_f.format(
        fxi=json_config["fxi"],
        fyi=json_config["fyi"],
        cx=json_config["cx"],
        cy=json_config["cy"],
        s=json_config["s"],
        configs=eqc_str
    )

    return text


if __name__ == "__main__":
    args = parser.parse_args()

    eqc_list = gen_eqc_list(args)
    config = gen_config(args, eqc_list)

    base_path = Path(f'monodromy/results/{args.config}/m2')
    base_path.mkdir(parents=True, exist_ok=True)

    # Write config.m2
    f = open(base_path / "config.m2", "w")
    f.write(config)
    f.close()

    # Write monodromy.m2
    shutil.copyfile("monodromy/m2/skew-2/monodromy.m2", base_path / "monodromy.m2")
