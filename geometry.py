import atom
import molecule

class Geometry:
    def __init__(self, matter = []):
        self.matter = matter
    def append(other):
        if isinstance(other, Geometry):
            self.matter += other.matter
        elif isinstance(other, molecule.Molecule) or isinstance(other, atom.Atom):
            self.matter.append(other)
        else:
            print "Error: don't know how to include", other, "in", self

