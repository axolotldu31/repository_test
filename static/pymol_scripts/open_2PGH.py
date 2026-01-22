import pymol
from pymol import cmd

pymol.finish_launching(['pymol', '-q'])

cmd.fetch('2PGH')
cmd.center('2PGH')
cmd.zoom('2PGH')
cmd.show('cartoon')
cmd.color('spectrum')
cmd.set('cartoon_fancy_helices', 1)
cmd.set('cartoon_fancy_sheets', 1)
cmd.bg_color('white')
