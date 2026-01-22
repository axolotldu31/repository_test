@echo off
echo Nettoyage du projet - Suppression des fichiers inutiles pour le site web...

REM Supprimer les fichiers Python inutiles
del /F /Q hello.py 2>nul
del /F /Q exemple_alignement.py 2>nul
del /F /Q test_pymol.py 2>nul
del /F /Q pymol_config.py 2>nul
del /F /Q rcsb_pdb_search.py 2>nul
del /F /Q read_csv.py 2>nul
del /F /Q requirements_desktop.txt 2>nul
del /F /Q RechercheProteines.spec 2>nul
del /F /Q analysis_sequences_fixed.ipynb 2>nul

REM Supprimer les fichiers PDB à la racine
del /F /Q 2pgh.pdb 2>nul
del /F /Q 3gou.pdb 2>nul
del /F /Q 3pel.pdb 2>nul
del /F /Q 6ihx.pdb 2>nul

REM Supprimer les fichiers CSV et JSON à la racine
del /F /Q aa_sequences_varlen.csv 2>nul
del /F /Q pdb_search_id_8WL6.csv 2>nul
del /F /Q pdb_search_results.csv 2>nul
del /F /Q proteins.json 2>nul

REM Supprimer les dossiers inutiles
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
rmdir /S /Q __pycache__ 2>nul
rmdir /S /Q site_recherche_proteines 2>nul
rmdir /S /Q fichiers_pdb 2>nul
rmdir /S /Q scripts_pymol 2>nul

echo.
echo ✓ Nettoyage terminé !
echo.
echo Fichiers conservés pour le site web :
echo - app.py
echo - requirements.txt
echo - templates/ (index.html, login.html, register.html)
echo - static/ (app.js, pdb_files/, pymol_scripts/, pymol_sessions/)
echo - donnees/ (utilisateurs_desktop.db, resultats_csv/)
echo.
pause
