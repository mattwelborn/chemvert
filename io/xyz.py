from ..matter import periodic_table
from ..matter import geometry
from ..matter import atom
import common

import numpy

def load(f):
    f = common.get_file_handle(f)
    natoms = int(f.readline())
    comment = f.readline().rstrip()

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
