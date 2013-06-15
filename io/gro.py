from ..matter import periodic_table
from ..matter import geometry
from ..matter import atom
from ..matter import gmx
import common
import re

import numpy

def load(f, rename_atoms = {}, rename_mol={}):
    f, washandle = common.get_file_read_handle(f)
    extras = {}
    comment = f.readline().rstrip()
    extras['comment'] = comment

    natoms = int(f.readline())

    geo = geometry.Geometry([])

    wmsplit = re.compile(r'(\d+)(\w+)')
    molnum_prev, mol_prev = -1,None
    for i in range(natoms):
        s = f.readline().split()
        
        # s[0] contains the molecule number and name
        m = wmsplit.search(s[0])
        molnum  = m.group(1)
        molname = m.group(2)
        # s[1] is the atom gmxname
        gmxname = s[1]
        if gmxname in rename_atoms:
            symbol = rename_atoms[gmxname]
        else:
            symbol = gmxname
        a = periodic_table.by_symbol(symbol)
        name = a.name if a else None
        number = a.number if a else None
        mass = a.mass if a else None
        

        # s[3:6] are coordinates in nm
        r = numpy.array(map(float, s[3:6])) * 10
        # s[6:10] are velocities in nm/ps
        v = numpy.array(map(float, s[6:10])) * 10
        atm = gmx.GMXAtom(symbol, name, number, mass, r, gmxname, v)
        
        if not mol_prev or molnum_prev != molnum:
            if mol_prev and molnum_prev != molnum:
                geo.append(mol_prev)
            symbol, name = rename_mol[molname] if molname in rename_mol else [None, None]
            mol = gmx.GMXMolecule([], symbol, name, molnum, molname)
        else:
            mol = mol_prev
        mol.append(atm)
        
        molnum_prev, mol_prev = molnum, mol

    geo.append(mol)     
    
    # last line is the box in nm
    geo.box = numpy.diag(numpy.array(map(float, f.readline().split()))*10)
    if not washandle:
        f.close()
    return geo, extras

def save(f, geo, extras = {}):
    f, washandle = common.get_file_write_handle(f)
    #TODO
