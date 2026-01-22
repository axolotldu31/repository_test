# Script PyMOL - Alignement de structures
# Protéines: 2PGH, 3PEL, 3GOU

# Charger toutes les structures
fetch 2PGH, async=0
fetch 3PEL, async=0
fetch 3GOU, async=0

# Afficher en cartoon
show cartoon, 2PGH
color cyan, 2PGH
show cartoon, 3PEL
color magenta, 3PEL
show cartoon, 3GOU
color yellow, 3GOU

# Alignement structural sur 2PGH (référence)
align 3PEL, 2PGH
align 3GOU, 2PGH

# Centrer et zoomer
center
zoom

# Paramètres d'affichage
set cartoon_fancy_helices, 1
set cartoon_fancy_sheets, 1
bg_color white
set seq_view, on

# Afficher le RMSD dans la console
print('RMSD 2PGH vs 3PEL:')
print('RMSD 2PGH vs 3GOU:')

# Légende des couleurs
# 2PGH: cyan
# 3PEL: magenta
# 3GOU: yellow
