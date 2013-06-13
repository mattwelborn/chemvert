# Periodic table gets atom data

import atom
import copy
import os

atoms = []
#auxillary dictionaries for effecient access
atoms_by_number = {}
atoms_by_symbol = {}
atoms_by_name = {}
for line in open(os.path.join(os.path.dirname(__file__), 'periodic_table')):
    s = line.split()
    number = int(s[2])
    name = s[1]
    symbol = s[0]
    mass = float(s[3])
    new_atom = atom.Atom(symbol, name, number, mass, None)
    atoms.append(new_atom)

    atoms_by_number[number] = new_atom
    atoms_by_symbol[symbol] = new_atom
    atoms_by_name[name]     = new_atom

def by_number(number):
    if number in atoms_by_number:
        return copy.deepcopy(atoms_by_number[number])
    else:
        return False
def by_name(name):
    if name in atoms_by_name:
        return copy.deepcopy(atoms_by_name[name])
    else:
        return False
def by_symbol(symbol):
    if symbol in atoms_by_symbol:
        return copy.deepcopy(atoms_by_symbol[symbol])
    else:
        return False
