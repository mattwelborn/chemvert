import atom
import molecule
import copy

class Geometry:
    def __init__(self, matter = [], box = []):
        self.matter = matter
        self.box = box
    def append(self, other):
        if isinstance(other, Geometry):
            self.matter += other.matter
        elif isinstance(other, molecule.Molecule) or isinstance(other, atom.Atom):
            self.matter.append(other)
        else:
            print "Error: don't know how to include", other, "in", self
            raise Exception()
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

    def get_molecules(self):
        return [i for i in self.matter if isinstance(i, molecule.Molecule)]
