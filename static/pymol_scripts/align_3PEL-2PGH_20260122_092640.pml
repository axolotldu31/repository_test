# Script PyMOL - Alignement de structures
# Protéines: 3PEL, 2PGH

# Charger toutes les structures
fetch 3PEL, async=0
fetch 2PGH, async=0

# Afficher en cartoon
show cartoon, 3PEL
color cyan, 3PEL
show cartoon, 2PGH
color magenta, 2PGH

# Alignement structural sur 3PEL (référence)
align 2PGH, 3PEL

# Centrer et zoomer
center
zoom

# Paramètres d'affichage
set cartoon_fancy_helices, 1
set cartoon_fancy_sheets, 1
bg_color white
set seq_view, on

# Afficher le RMSD dans la console
print('RMSD 3PEL vs 2PGH:')

# Légende des couleurs
# 3PEL: cyan
# 2PGH: magenta
