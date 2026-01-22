#!/bin/bash

echo "Nettoyage du projet - Suppression des fichiers inutiles pour le site web..."

# Supprimer les fichiers Python inutiles
rm -f hello.py
rm -f exemple_alignement.py
rm -f test_pymol.py
rm -f pymol_config.py
rm -f rcsb_pdb_search.py
rm -f read_csv.py
rm -f requirements_desktop.txt
rm -f RechercheProteines.spec
rm -f analysis_sequences_fixed.ipynb

# Supprimer les fichiers PDB à la racine
rm -f 2pgh.pdb
rm -f 3gou.pdb
rm -f 3pel.pdb
rm -f 6ihx.pdb

# Supprimer les fichiers CSV et JSON à la racine
rm -f aa_sequences_varlen.csv
rm -f pdb_search_id_8WL6.csv
rm -f pdb_search_results.csv
rm -f proteins.json

# Supprimer les dossiers inutiles
rm -rf build/
rm -rf dist/
rm -rf __pycache__/
rm -rf site_recherche_proteines/
rm -rf fichiers_pdb/
rm -rf scripts_pymol/

echo ""
echo "✓ Nettoyage terminé !"
echo ""
echo "Fichiers conservés pour le site web :"
echo "- app.py"
echo "- requirements.txt"
echo "- templates/ (index.html, login.html, register.html)"
echo "- static/ (app.js, pdb_files/, pymol_scripts/, pymol_sessions/)"
echo "- donnees/ (utilisateurs_desktop.db, resultats_csv/)"
echo ""
