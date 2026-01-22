import pymol
from pymol import cmd

pymol.finish_launching(['pymol', '-q'])

cmd.fetch('8WL6')
cmd.center('8WL6')
cmd.zoom('8WL6')
cmd.show('cartoon')
cmd.color('spectrum')
cmd.set('cartoon_fancy_helices', 1)
cmd.set('cartoon_fancy_sheets', 1)
cmd.bg_color('white')
