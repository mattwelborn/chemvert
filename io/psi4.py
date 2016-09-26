import common
from ..matter import geometry,periodic_table

import os
import numpy


def load_output(fl):
    f, washandle = common.get_file_read_handle(fl)
    stuff = {}
    stuff['done'] = False
    stuff['energies'] = []
    stuff['n_electrons'] = None
    stuff['n_basis'] = None
    stuff['overlaps'] = []
    stuff['1e_ints'] = []
    stuff['2e_ints'] = []
    stuff['nuclear_repulsion'] = None
    stuff['final_geo'] = None
    stuff['geos'] = []

    def read_done(trigger_line):
        if not "PSI4 exiting successfully. Buy a developer a beer!" in line:
            return False
        stuff['done'] = True
        return True

    def read_nuclear_repulsion(trigger_line):
        if not "Nuclear repulsion energy" in line:
            return False
        stuff['nuclear_repulsion'] = float(trigger_line.split()[-1])
        return True

    def read_energetics(trigger_line):
        if not "=> Energetics <=" in line:
            return False
        ergs = {}
        f.readline()
        # XXX: should use a map here instead of relying on ordering
        ergs['nuclear_repulsion'] = float(f.readline().split()[-1])
        ergs['one'] = float(f.readline().split()[-1])
        ergs['two'] = float(f.readline().split()[-1])
        ergs['XC'] = float(f.readline().split()[-1])
        ergs['empirical_dispersion'] = float(f.readline().split()[-1])
        ergs['PCM'] = float(f.readline().split()[-1])
        ergs['EFP'] = float(f.readline().split()[-1])
        ergs['total'] = float(f.readline().split()[-1])

        stuff['energies'].append(ergs)
        return True

    def read_nelectrons(trigger_line):
        if not "Electrons" in line:
            return False
        stuff['n_electrons'] = int(trigger_line.split()[-1])
        return True

    def read_basis(trigger_line):
        if not "==> Primary Basis <==" in trigger_line:
            return False
        f.readline()
        f.readline()
        f.readline()
        line = f.readline()
        assert("Number of basis function" in line)
        stuff['n_basis'] = int(line.split()[-1])
        return True

    def _read_psimat(n):
        f.readline()
        M = numpy.zeros((n,n))
        pos = 0
        while True:
            f.readline()
            width = len(f.readline().split())
            f.readline()
            for i in range(n):
                line = f.readline()
                vals = numpy.array(map(float, line.split()[1:]))
                M[i,pos:pos+width] = vals
            pos += width
            if pos == n:
                break
        return M

    def read_overlap(trigger_line):
        if not "## Overlap" in trigger_line:
            return False
        stuff['overlaps'] = _read_psimat(stuff['n_basis'])
        return True

    def read_1e_ints(trigger_line):
        if not "## One Electron Ints" in trigger_line:
            return False
        stuff['1e_ints'] = _read_psimat(stuff['n_basis'])
        return True

    def read_dipole(trigger_line):
        if not "## AO Dipole" in trigger_line:
            return False
        which = trigger_line.split()[3].lower()
        stuff['dipole_%s' % which] = _read_psimat(stuff['n_basis'])
        return True

    def read_2e_ints(trigger_line):
        if not "Two-electron Integrals" in trigger_line:
            return False
        n = stuff['n_basis']
        V = numpy.zeros((n,n,n,n))
        f.readline()
        while True:
            line = f.readline()
            if not '(' in line:
                break
            braket, val = line.split('=')
            val = float(val)
            ijkl = braket.replace('(',' ').replace(')',' ').replace('|',' ')
            i,j,k,l = map(int, ijkl.split())

            # Chem -> phys notation
            k,j = j,k

            V[i,j,k,l] = val
            V[j,i,l,k] = val
            V[k,l,i,j] = val
            V[l,k,j,i] = val
            V[k,j,i,l] = val
            V[l,i,j,k] = val
            V[i,l,k,j] = val
            V[j,k,l,i] = val

        stuff['2e_ints'] = V
        return True

    def read_final_geom(trigger_line):
        if not "Final optimized geometry and variables:" in trigger_line:
            return False

        for i in range(5): f.readline()

        geo = geometry.Geometry([])
        while True:
            line = f.readline()
            if not line or len(line.split()) == 0:
                break

            s = line.split()
            symbol = s[0]
            a = periodic_table.by_symbol(symbol)
            if not a:
                a = atom.Atom(symbol, None, None, None, None)

            r = numpy.array(map(float, s[1:4]))
            a.r = r
            geo.append(a)

        stuff['final_geo'] = geo
        return True
        



    allparsers = [read_done, read_nuclear_repulsion, read_energetics, read_nelectrons, read_basis, read_overlap, read_1e_ints, read_2e_ints, read_dipole, read_final_geom]
    while True: #parsing loop
        line = f.readline()
        if not line:
            break

        for parse in allparsers:
            if parse(line):
                break

    if not washandle: f.close()

    return stuff
