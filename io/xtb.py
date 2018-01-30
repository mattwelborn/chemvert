from ..matter import periodic_table
from ..matter import geometry
from ..matter import atom
import common

import numpy

def load(f):
    f, wasfile = common.get_file_read_handle(f)
    line = f.readline()
    if not line:
        return None,None
    natoms = int(line)
    comment = f.readline().rstrip()
    extras = {}
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
        geo.append(a)

    if not wasfile:
        f.close()
    return geo, extras

def save(f, geo, extras = {}):
    f, washandle = common.get_file_write_handle(f)
    allatoms = geo.get_atoms()
    print >> f, "$coord"

    for i in allatoms:
        print >> f, i.r[0]/0.529177, i.r[1]/0.529177, i.r[2]/0.529177, ''.join([q for q in i.symbol if not q.isdigit()])
    print >>f, "$end"

    if not washandle:
        f.close()

