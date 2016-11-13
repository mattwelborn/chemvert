import numpy
import fortranformat as ff

from ..matter import periodic_table
from ..matter import geometry
from ..matter import atom
import common

angstrom_to_bohr = 1.889725989
bohr_to_angstrom = 0.529177249

def load(f):
    f, washandle = common.get_file_read_handle(f)

    grid = numpy.zeros((3,3))
    npts = numpy.zeros(3,dtype=numpy.int_)
    extras = {}

    extras['header'] = f.readline().rstrip()
    extras['kind'] = f.readline().rstrip()
    s = f.readline().split()
    natoms = int(s[0])
    origin = numpy.array(map(float,s[1:4])) * bohr_to_angstrom
    for i in range(3):
        s = f.readline().split()
        npts[i] = int(s[0])
        grid[i,:] = numpy.array(map(float,s[1:4])) * bohr_to_angstrom

    geo = geometry.Geometry([])
    for i in range(natoms):
        s = f.readline().split()
        number = int(s[0])
        a = periodic_table.by_number(number)
        if not a:
            a = atom.Atom(None, None, number, None, None)
        r = numpy.array(map(float, s[2:5])) * bohr_to_angstrom
        a.r = r
        geo.append(a)

    data = numpy.zeros(npts[0]*npts[1]*npts[2])
    count = 0
    for line in f:
        d = map(float, line.replace('D','E').split())
        for z in d:
            data[count] = z
            count += 1

    count = 0
    p = numpy.zeros(npts)
    for i in range(npts[0]):
        for j in range(npts[1]):
            for k in range(npts[2]):
                p[i,j,k] = data[count]
                count += 1

    if not washandle:
        f.close()

    return geo, p, origin, grid, npts, extras


def save(f, geo, p, origin, grid, npts, extras = None):
    f, washandle = common.get_file_write_handle(f)
    origin_writer = ff.FortranRecordWriter('I5,3F12.6')
    grid_writer   = ff.FortranRecordWriter('I5,3F12.6')
    val_writer    = ff.FortranRecordWriter('6E13.5')
    atom_writer   = ff.FortranRecordWriter('I5,4F12.6')

    if extras is not None and 'header' in extras:
        print >> f, extras['header']
    else:
        print >> f, "Created by chemvert"

    if extras is not None and 'kind' in extras:
        print >> f, extras['kind']
    else:
        print >> f, "Unknown"

    borigin = origin * angstrom_to_bohr
    a = grid[0,:] * angstrom_to_bohr
    b = grid[1,:] * angstrom_to_bohr
    c = grid[2,:] * angstrom_to_bohr
    
    na,nb,nc = npts
    natoms = len(geo.get_atoms())
    print >> f, origin_writer.write([natoms,borigin[0],borigin[1],borigin[2]])
    print >> f, grid_writer.write([na, a[0], a[1], a[2]])
    print >> f, grid_writer.write([nb, b[0], b[1], b[2]])
    print >> f, grid_writer.write([nc, c[0], c[1], c[2]])
    for atom in geo.get_atoms():
        r = atom.r * angstrom_to_bohr
        print >> f, atom_writer.write([atom.number, 0.0, r[0], r[1], r[2]])
    for i in range(na):
        for j in range(nb):
            for chunk in chunks(p[i,j,:], 6):
                print >> f, val_writer.write(chunk)
            

    if not washandle:
        f.close()

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

if __name__ == '__main__':
    import chemvert
    import sys
    geo, p, origin, grid, npts, extras = chemvert.io.cube.load(sys.argv[1])
    chemvert.io.cube.save(sys.argv[1]+'.idem', geo, p, origin, grid, npts, extras)

