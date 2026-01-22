# Script PyMOL - Alignement de structures
# Protéines: 5C6E, 2QSP, 1G09, 1G0A, 3GOU, 3PEL, 6IHX

# Charger toutes les structures
fetch 5C6E, async=0
fetch 2QSP, async=0
fetch 1G09, async=0
fetch 1G0A, async=0
fetch 3GOU, async=0
fetch 3PEL, async=0
fetch 6IHX, async=0

# Afficher en cartoon
show cartoon, 5C6E
color cyan, 5C6E
show cartoon, 2QSP
color magenta, 2QSP
show cartoon, 1G09
color yellow, 1G09
show cartoon, 1G0A
color salmon, 1G0A
show cartoon, 3GOU
color lime, 3GOU
show cartoon, 3PEL
color orange, 3PEL
show cartoon, 6IHX
color purple, 6IHX

# Alignement structural sur 5C6E (référence)
align 2QSP, 5C6E
align 1G09, 5C6E
align 1G0A, 5C6E
align 3GOU, 5C6E
align 3PEL, 5C6E
align 6IHX, 5C6E

# Centrer et zoomer
center
zoom

# Paramètres d'affichage
set cartoon_fancy_helices, 1
set cartoon_fancy_sheets, 1
bg_color white
set seq_view, on

# Afficher le RMSD dans la console
print('RMSD 5C6E vs 2QSP:')
print('RMSD 5C6E vs 1G09:')
print('RMSD 5C6E vs 1G0A:')
print('RMSD 5C6E vs 3GOU:')
print('RMSD 5C6E vs 3PEL:')
print('RMSD 5C6E vs 6IHX:')

# Légende des couleurs
# 5C6E: cyan
# 2QSP: magenta
# 1G09: yellow
# 1G0A: salmon
# 3GOU: lime
# 3PEL: orange
# 6IHX: purple
