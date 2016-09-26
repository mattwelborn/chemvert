import common
from ..matter import geometry,periodic_table

import os
import numpy

class QChemOptions:
    def __init__(self, charge=0, spin=1):
        self.charge = charge
        self.spin   = spin
        self.rem    = {}
        self.extras = ""
    def rem_str(self):
        ret = ""
        for key in self.rem:
            ret += "%s %s\n" % (key, self.rem[key])
        return ret

def load(fl):
    f, washandle = common.get_file_read_handle(fl)

    geo = geometry.Geometry()
    opts = QChemOptions()
    
    def read_molecule(trigger_line):
        if not '$molecule' in trigger_line:
            return False
        opts.charge, opts.spin = map(int, f.readline().split())
        while True:
            line = f.readline()
            if '$end' in line or not line or '@@@' in line:
                break
            s = line.split()
            symbol = s[0]
            a = periodic_table.by_symbol(symbol)
            a.r = numpy.array(map(float, s[1:4]))
            geo.append(a)
        return True
    
    def read_rem(trigger_line):
        if not '$rem' in trigger_line:
            return False
        while True:
            line = f.readline()
            if '$end' in line or not line or '@@@' in line:
                break
            s = line.split()
            if len(s) == 0:
                continue
            opts.rem[s[0]] = s[1]
        return True
    
    allparsers = [read_molecule, read_rem]
    while True: #parsing loop
        line = f.readline()
        if not line or line.startswith('@@@'):
            break

        for parse in allparsers:
            if parse(line):
                break

    if not washandle: f.close()

    return geo, opts


def save(fl, geo, options, rename = {}, delete = []):
    f, washandle = common.get_file_write_handle(fl)

    print >> f, "$molecule"
    print >> f, options.charge, options.spin
    for i in geo.get_atoms():
        if i.symbol in delete:
            continue
        symbol = rename[i.symbol] if i.symbol in rename else i.symbol
        print >> f, symbol, i.r[0], i.r[1], i.r[2]
    print >> f, "$end"
    print >> f
    print >> f, "$rem"
    print >> f, options.rem_str()
    print >> f, "$end"
    print >> f
    print >> f, options.extras
    print >> f

    if not washandle: f.close()

def load_output(fl,nowarn=False):
    f, washandle = common.get_file_read_handle(fl)
    stuff = {}
    stuff['geos'] = []
    stuff['done'] = False
    stuff['energies'] = []
    stuff['mulliken'] = []
    stuff['chelpg'] = []
    stuff['hirshfeld'] = []
    stuff['cdftci'] = None
    stuff['n_electrons'] = {}
    stuff['n_basis'] = None
    stuff['n_cart_basis'] = None
    stuff['overlaps'] = []
    stuff['1e_ints'] = []
    stuff['2e_ints'] = []
    stuff['nuclear_repulsion'] = None
    stuff['rho_as'] = []
    stuff['rho_bs'] = []
    stuff['fock_as'] = []
    stuff['fock_bs'] = []
    stuff['multipoles'] = {}
    stuff['MO_energies'] = []
    stuff['NPA'] = []

    def read_starfleet(trigger_line):
        if not 'Thank you very much for using Q-Chem.  Have a nice day.' in trigger_line:
            return False

        stuff['done'] = True
        return True

    # Reads charge and spin from echo of input file
    # might be janky
    def read_charge_spin(trigger_line):
        if not '$molecule' in trigger_line:
            return False
        charge, spin = map(int, f.readline().split())
        stuff['charge'] = charge
        stuff['spin']   = spin
        return True

    def read_convergence_fail(trigger_line):
        if not 'SCF failed to converge' in trigger_line:
            return False
        stuff['convergence_fail'] = True
        return True

    def read_final_energy(trigger_line):
        if not 'Final energy is' in trigger_line:
            return False
        stuff['energies'].append(float(trigger_line.split()[-1]))
        return True

    def read_energy(trigger_line):
        if not 'Total energy in the final basis set' in trigger_line:
            return False
        stuff['energies'].append(float(trigger_line.split()[-1]))
        return True

    def read_nuclear_repulsion(trigger_line):
        if not 'Nuclear Repulsion Energy' in trigger_line:
            return False
        stuff['nuclear_repulsion'] = float(trigger_line.split()[4])
        return True

    def read_nelectrons(trigger_line):
        if not ("There are" in trigger_line and "beta electrons" in trigger_line):
            return False
        na = int(trigger_line.split()[2])
        nb = int(trigger_line.split()[5])
        stuff['n_electrons'] = {'alpha': na, 'beta': nb}
        return True

    def read_nbasis(trigger_line):
        if not ("There are" in trigger_line and "basis functions" in trigger_line):
            return False
        nbasis = int(trigger_line.split()[5])
        stuff['n_basis'] = nbasis
        return True

    def read_n_cart_basis(trigger_line):
        if not ("Number of Cartesian basis functions" in trigger_line):
            return False
        nbasis = int(trigger_line.split()[-1])
        stuff['n_cart_basis'] = nbasis
        return True



    def _read_qcmat(n):
        M = numpy.zeros((n,n))
        pos = 0
        while True:
            width = len(f.readline().split())
            for i in range(n):
                line = f.readline()
                vals = numpy.array(map(float, line.split()[1:]))
                M[i,pos:pos+width] = vals
            pos += width
            if pos == n:
                break
        return M

    def read_npa(trigger_line):
        if not ("Summary of Natural Population Analysis" in trigger_line):
            return False
        for i in range(5):
            f.readline()
        charges = []
        spins = []
        while True:
            line = f.readline()
            if not line or '============' in line:
                break
            s = line.split()
            charges.append(float(s[2]))
            spins.append(float(s[-1]))
        charges = numpy.array(charges)
        spins = numpy.array(spins)
        stuff['NPA'].append({'charge':charges,'spin':spins})

    def read_multipole(trigger_line):
        if not 'Multipole Matrix' in trigger_line:
            return False
        which = trigger_line.split()[-1]
        stuff['multipoles'][which] = _read_qcmat(stuff['n_basis'])
        return True

    def read_overlap(trigger_line):
        if not 'Overlap Matrix' in trigger_line:
            return False
        stuff['overlaps'].append(_read_qcmat(stuff['n_basis']))
        return True

    def read_rho_a(trigger_line):
        if not 'Alpha Density Matrix' in trigger_line:
            return False
        stuff['rho_as'].append(_read_qcmat(stuff['n_basis']))
        return True

    def read_rho_b(trigger_line):
        if not 'Beta Density Matrix' in trigger_line:
            return False
        stuff['rho_bs'].append(_read_qcmat(stuff['n_basis']))
        return True

    def read_fock_a(trigger_line):
        if not 'Calculated Alpha Fock Matrix' in trigger_line:
            return False
        stuff['fock_as'].append(_read_qcmat(stuff['n_basis']))
        return True

    def read_fock_b(trigger_line):
        if not 'Calculated Beta Fock Matrix' in trigger_line:
            return False
        stuff['fock_bs'].append(_read_qcmat(stuff['n_basis']))
        return True


    def read_1e_ints(trigger_line):
        if not 'Core Hamiltonian Matrix' in trigger_line:
            return False
        stuff['1e_ints'].append(_read_qcmat(stuff['n_basis']))
        return True

    def read_2e_ints(trigger_line):
        if not 'AOInts used' in trigger_line:
            return False

        if not stuff['n_basis'] == stuff['n_cart_basis']:
            print "Number of basis and Cartesian basis function unequal"
            print "Not sure what to do"
            return False

        n = stuff['n_basis']
        V = numpy.zeros((n,n,n,n))
        while True:
            line = f.readline()
            if not line.startswith(" ("):
                break

            idxs, val = line.split('=')
            val = float(val)
            ij,kl = idxs.split('|')
            ij = ij.split('(')[1]
            kl = kl.split(')')[0]
            i,j = numpy.array(map(int, ij.split(',')))-1
            k,l = numpy.array(map(int, kl.split(',')))-1

            j,k = k,j # swap chemists' -> physicists' notation

            try:
                V[i,j,k,l] = val
                V[j,i,l,k] = val
                V[k,l,i,j] = val
                V[l,k,j,i] = val
                V[k,j,i,l] = val
                V[l,i,j,k] = val
                V[i,l,k,j] = val
                V[j,k,l,i] = val
            except(IndexError):
                print line
                print i,j,k,l


        stuff['2e_ints'].append(V)

        return True

    def read_MO_energies(trigger_line):
        if not "Alpha MOs" in trigger_line:
            return False
        ao = []
        av = []
        ret = {}
        f.readline()
        # Alpha occupied
        while True:
            line = f.readline()
            if "-- Virtual --" in line:
                break
            try:
                ao += map(float, line.split())
            except ValueError:
                if not nowarn:
                    print "Warning: bad line in MOs"
                    print line
                ao = [] 
        # Alpha virtual
        while True:
            line = f.readline()
            if "---------" in line or not line or len(line.split())==0:
                break
            try:
                av += map(float, line.split())
            except ValueError:
                if not nowarn:
                    print "Warning: bad line in MOs"
                    print line
                av = []
        ret['alpha'] = {'occupied': numpy.array(ao), 'virtual': numpy.array(av)}


        line = f.readline()
        if "Beta MOs" in line:
            bo = []
            bv = []
            f.readline()
            # Beta occupied
            while True:
                line = f.readline()
                if "-- Virtual --" in line:
                    break
                try:
                    bo += map(float, line.split())
                except ValueError:
                    if not nowarn:
                        print "Warning: bad line in MOs"
                        print line
                    bo = []
            # Beta virtual
            while True:
                line = f.readline()
                if "---------" in line or not line:
                    break
                try:
                    bv += map(float, line.split())
                except ValueError:
                    if not nowarn:
                        print "Warning: bad line in MOs"
                        print line
                    bv = []
            ret['beta'] = {'occupied': numpy.array(bo), 'virtual': numpy.array(bv)}

        stuff['MO_energies'].append(ret)
        return True


    def read_chelpg(trigger_line):
        if not "Ground-State ChElPG Net Atomic Charges" in trigger_line:
            return False
        f.readline()
        f.readline()
        f.readline()

        charges = []
        while True:
            line = f.readline()
            if '------------------' in line:
                break

            s = line.split()
            charges.append(float(s[2]))

        charges = numpy.array(charges)

        stuff['chelpg'].append(charges)
        return True

    def read_hirshfeld(trigger_line):
        if not "Hirshfeld Atomic Charges" in trigger_line:
            return False
        f.readline()
        f.readline()
        f.readline()

        charges = []
        while True:
            line = f.readline()
            if '------------------' in line:
                break

            s = line.split()
            charges.append(float(s[2]))

        charges = numpy.array(charges)

        stuff['hirshfeld'].append(charges)
        return True


    def read_mulliken(trigger_line):
        if not "Ground-State Mulliken Net Atomic Charges" in trigger_line:
            return False
        f.readline()
        f.readline()
        f.readline()

        charges = []
        while True:
            line = f.readline()
            if '------------------' in line:
                break

            s = line.split()
            charges.append(float(s[2]))

        charges = numpy.array(charges)

        stuff['mulliken'].append(charges)
        return True

    def read_standard(trigger_line):
        if not "Standard Nuclear Orientation" in trigger_line:
            return False
        f.readline()
        f.readline()

        geo = geometry.Geometry([])
        while True:
            line = f.readline()
            if '------------------' in line:
                break

            s = line.split()
            symbol = s[1]
            a = periodic_table.by_symbol(symbol)
            if not a:
                a = atom.Atom(symbol, None, None, None, None)

            r = numpy.array(map(float, s[2:5]))
            a.r = r
            geo.append(a)

        stuff['geos'].append(geo)
        return True

    def read_cdftci(trigger_line):
        if not "CDFT-CI Hamiltonian matrix in orthogonalized basis" in trigger_line:
            return False
        nstates = len(f.readline().split())
        H = numpy.zeros((nstates,nstates))
        for i in range(nstates):
            line = f.readline()
            line = line.replace('-',' -') # fix qchem runons
            H[i,:] = map(float, line.split()[1:])
        stuff['cdftci'] = H
        return True




    allparsers = [read_starfleet, read_final_energy, read_energy, read_standard, read_mulliken, read_cdftci, read_overlap, read_nuclear_repulsion, read_1e_ints, read_2e_ints, read_nbasis, read_nelectrons, read_n_cart_basis, read_rho_a, read_rho_b, read_fock_a, read_fock_b, read_multipole, read_MO_energies, read_chelpg, read_hirshfeld, read_npa, read_charge_spin, read_convergence_fail]
    while True: #parsing loop
        line = f.readline()
        if not line or line.startswith('@@@'):
            break

        for parse in allparsers:
            if parse(line):
                break

    if not washandle: f.close()

    return stuff

    


