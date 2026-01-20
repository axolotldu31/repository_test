import json
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--csv",)
parser.add_argument("--json",)
parser.add_argument("--seq",)
args = parser.parse_args()

sequences_list = []

if args.csv:
    with open(args.csv) as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for row in csv_reader:
            sequences_list.append(row[1])
elif args.json:
    with open(args.json) as f:
        data = json.load(f)

        for protein in data["proteins"]:
            sequence = protein["meta"]["sequence"]
            sequences_list.append(sequence)
elif args.seq:
    sequence = args.seq
    sequences_list.append(sequence)

def compute_sequence_length(sequences: list):
    for sequence in sequences:
        nombre_caracteres = len(sequence)
        print(f"{sequence} a {nombre_caracteres} caracteres")

compute_sequence_length(sequences_list)