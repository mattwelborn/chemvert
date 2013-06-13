from ..matter import periodic_table
from ..matter import geometry
from ..matter import atom
import common

import numpy

def load(f):
    f = common.get_file_handle(f)
    natoms = int(f.readline())
    comment = f.readline().rstrip()
    extras['comment'] = comment

    geo = geometry.Geometry([])
    for i in range(natoms):
        s = f.readline().split()
        symbol = s[0]
        a = periodic_table.by_symbol(symbol)
        if not a:
            a = atom.Atom(symbol, None, None, None, None)

        r = numpy.array(map(float, s[1:4]))
        a.r = r
        geo += a

    f.close()
    return geo, extras

def save(f, geo, extras = {}):
    f, washandle = common.get_file_write_handle(f)
    allatoms = geo.get_atoms()
    print >> f, len(atoms)
    if 'comment' in extras:
        print >> f, extras['comment']
    else:
        print >> f, "Generated by struct"

    for i in atoms:
        print >> f, i.symbol, i.r[0], i.r[1], i.r[2]

    if not washangle:
        f.close()

