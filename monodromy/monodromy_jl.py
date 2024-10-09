import argparse
import json
from pathlib import Path
import shutil

import pandas as pd

parser = argparse.ArgumentParser(
    description='Runs monodromy for the chosen configuration on all equivalence classes.')

parser.add_argument(
    "--config",
    type=str,
    required=True,
    help="The calibration configuration."
)
parser.add_argument(
    "--variant",
    type=str,
    default="v2",
    help="The variant of the monodromy algorithm."
)


def gen_eqc_list(args):
    eqc_list = []

    # Load csv
    df = pd.read_csv(f"isomorphism/results/{args.config}/sym1/sym1.csv")
    for i, r in df.iterrows():
        if not r['is_singular']:
            eqc = r['rmv'].replace("[", "").replace("]", "").split(";")
            eqc_list.append(eqc)

    return eqc_list


def gen_config(args, eqc_list):
    # Read template config
    f = open(f"monodromy/jl/{args.variant}/config.jl", "r")
    config_f = f.read()

    # Read JSON config
    json_file = open('combinatorics/configs.json')
    json_config = json.load(json_file)['configs'][args.config]
    json_file.close()

    # Generate configuration list for Julia
    eqc_str = ""
    for eqc in eqc_list:
        if len(eqc_str) > 0:
            eqc_str += ","
        eqc_str += "[" + ",".join(eqc) + "]"

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

    base_path = Path(f'monodromy/results/jl/{args.config}/jl')
    base_path.mkdir(parents=True, exist_ok=True)

    # Write config.jl
    f = open(base_path / "config.jl", "w")
    f.write(config)
    f.close()

    # Write monodromy.jl
    shutil.copyfile(f"monodromy/jl/{args.variant}/monodromy.jl", base_path / "monodromy.jl")

    # Write utils.jl
    shutil.copyfile(f"monodromy/jl/{args.variant}/utils.jl", base_path / "utils.jl")
