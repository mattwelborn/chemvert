import atom
import molecule

class GMXAtom(atom.Atom):
    def __init__(self, symbol, name, number, mass, r, gmxname, v):
        atom.Atom.__init__(self, symbol, name, number, mass, r)
        self.gmxname = gmxname
        self.v = v


class GMXMolecule(molecule.Molecule):
    def __init__(self, atoms, symbol, name, gmxnum, gmxsymbol):
        molecule.Molecule.__init__(self, atoms, symbol, name)
        self.gmxnum = gmxnum
        self.gmxsymbol = gmxsymbol

