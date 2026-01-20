import json

with open("/mnt/c/Users/axelg/Downloads/proteins.json") as f:
    data = json.load(f)

for protein in data["proteins"]:
    sequence = protein["meta"]["sequence"]
    nombre_caracteres = len(sequence)
    name = protein["name"]
    print(name,":", nombre_caracteres)
    
    