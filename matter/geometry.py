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
    def get_atoms(self):
        ret = []
        for i in self.matter:
            if isinstance(i, atom.Atom):
                ret.append(i)
            elif isinstance(i, molecule.Molecule):
                ret += i.get_atoms()
            else:
                print "Error: found non atom or molecule in geometry"
        return ret

