import atom
import molecule
import copy

class Geometry:
    def __init__(self, matter = []):
        self.matter = matter
    def append(self, other):
        if isinstance(other, Geometry):
            self.matter += other.matter
        elif isinstance(other, molecule.Molecule) or isinstance(other, atom.Atom):
            self.matter.append(other)
        else:
            print "Error: don't know how to include", other, "in", self
    def __add__(self, other):
        return copy.deepcopy(self).append(other)

