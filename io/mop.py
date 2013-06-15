from ..matter import periodic_table
from ..matter import geometry
from ..matter import atom
from ..matter import gmx
import common
import re

import numpy

def load(f):
    f, washandle = common.get_file_read_handle(f)
    extras['opts'] = f.readline().rstrip()
    f.readline()
    f.readline()

    geo = geometry.Geometry([])
    box = []
    for line in f:
        #TODO: weird * syntax
        s = line.split()
        if s[0] == 'Tv':
            box.append(map(float, s[1:4]))
        else:
            a = periodic_table.by_symbol(s[0])
            a.r = map(float, s[1:4])
            geo += a
    geo.box = numpy.array(box)
    if not washandle:
        f.close()
    return geo, extras

def save(f, geo, extras={}):
    f, washandle = common.get_file_write_handle(f)

    print >> f, extras['opts']
    print >> f
    print >> f
    for a in geo.get_atoms():
        print >> f, a.symbol, a.r[0], a.r[1], a.r[2]
    if hasattr(geo, 'box') and geo.box:
        print >> f, 'Tv', geo.box[0][0], geo.box[0][1], geo.box[0][2]
        print >> f, 'Tv', geo.box[1][0], geo.box[1][1], geo.box[1][2]
        print >> f, 'Tv', geo.box[2][0], geo.box[2][1], geo.box[2][2]

    if not washandle: f.close()


        



