#!/usr/bin/env python3
import argparse
import json
import csv
import sys
from collections import Counter
from pathlib import Path


def lire_sequences_json(chemin_fichier):
    """Lit les séquences depuis un fichier JSON."""
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # On suppose que le JSON contient une liste de séquences
        # ou un dictionnaire avec une clé 'sequences'
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'sequences' in data:
            return data['sequences']
        # Si c'est un dictionnaire, prendre les valeurs
        elif isinstance(data, dict):
            return list(data.values())
        else:
            return [data]
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier JSON: {e}")
        sys.exit(1)


def lire_sequences_csv(chemin_fichier):
    """Lit les séquences depuis un fichier CSV."""
    sequences = []
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip header if exists
            header = next(reader, None)

            for row in reader:
                # On prend la première colonne comme séquence
                if row:
                    sequences.append(row[0])
        return sequences
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier CSV: {e}")
        sys.exit(1)
    
def compter_sequences(sequences):
    """Compte les occurrences de chaque séquence."""
    return Counter(sequences)

def afficher_resultats(compteur):
    """Affiche chaque séquence avec son nombre d'occurrences."""
    print("\n" + "="*50)
    print("RÉSULTATS DU COMPTAGE")
    print("="*50 + "\n")
    
    for sequence, compte in compteur.items():
        print(f"Séquence: {sequence}")
        print(f"Nombre d'occurrences: {compte}")
        print("-" * 30)
    
    print(f"\nTotal de séquences uniques: {len(compteur)}")
    print(f"Total de séquences: {sum(compteur.values())}")
def main():
    parser = argparse.ArgumentParser(
        description='Compte les occurrences de séquences depuis différentes sources.'
    )

    # Groupe mutuellement exclusif pour les sources
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--json', type=str, help='Chemin vers un fichier JSON')
    group.add_argument('--csv', type=str, help='Chemin vers un fichier CSV')
    group.add_argument('--sequence', type=str, help='Séquence directe à analyser')

    args = parser.parse_args()

    sequences = []
    
    if args.json:
        print(f"Lecture du fichier JSON: {args.json}")
        sequences = lire_sequences_json(args.json)
        print(f"✓ Fichier JSON lu avec succès ({len(sequences)} séquences)")

    elif args.csv:
        print(f"Lecture du fichier CSV: {args.csv}")
        sequences = lire_sequences_csv(args.csv)
        print(f"✓ Fichier CSV lu avec succès ({len(sequences)} séquences)")

    elif args.sequence:
        print("Analyse de la séquence directe")
        sequences = [args.sequence]

    # Compter les séquences
    compteur = compter_sequences(sequences)
    
    # Afficher les résultats
    afficher_resultats(compteur)


if __name__ == "__main__":
    main()
