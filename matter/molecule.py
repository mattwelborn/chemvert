import atom
import copy

class Molecule:
    def __init__(self, atoms, symbol, name):
        self.atoms = atoms
        self.name = name
        self.symbol = symbol
    def r(self):
        return #TODO
    def get_atoms(self):
        return self.atoms
    def append(self, a):
        assert isinstance(a, atom.Atom)
        self.atoms.append(a)
    #def __add__(self, a):
    #    assert isinstance(a, atom.Atom)
    #    self.atoms.append(a)
    #    copy.

            
