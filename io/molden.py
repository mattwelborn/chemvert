import common
from ..matter import geometry,periodic_table
from ..orbital import ao

import os
import numpy


def load(fl,nowarn=False):
    f, washandle = common.get_file_read_handle(fl)

    stuff = {}
    stuff['geo'] = None
    stuff['basis'] = None
    stuff['orbitals'] = None


    linebuf = []

    def read_geo(trigger_line):
        if not "[Atoms]" in trigger_line:
            return False
        if "Angs" in trigger_line:
            coord_scale = 1.0
        else: #TODO: bohr detection and conversion
            raise NotImplementedError()

        geo = geometry.Geometry()
        while True:
            line = f.readline()
            linebuf.append(line)
            if not line or "[" in line:
                break
            linebuf.pop()

            s = line.split()
            symbol = s[0].capitalize()
            a = periodic_table.by_symbol(symbol)
            if not a:
                a = atom.Atom(symbol, None, None, None, None)

            r = numpy.array(map(float, s[3:6])) * coord_scale
            a.r = r
            a.molden_number = s[1] # For matching with basis functions
            geo.append(a)

        stuff['geo'] = geo

        return True

    def read_basis(trigger_line):
        # TODO: Maybe do STOs? 
        if not "[GTO]" in trigger_line:
            return False
        basis = []
        # Loop over atoms
        while True:
            line = f.readline()
            linebuf.append(line)
            if "[" in line:
                break
            linebuf.pop()

            if len(line.split()) == 0:
                continue
            molden_number = line.split()[0]
            # Loop over basis functions
            while True:
                line = f.readline()
                if not line or len(line.split()) == 0:
                    break
                s = line.split()
                shell = s[0]
                ncontract = int(s[1])
                # Loop over gaussians in contraction
                cs = numpy.zeros(ncontract)
                alphas = numpy.zeros(ncontract)
                for i in range(ncontract):
                    line = f.readline()
                    s = line.split()
                    cs[i] = numpy.float(s[1].replace('D','E'))
                    alphas[i] = numpy.float(s[0].replace('D','E'))

                bs = ao.make_shell(shell, cs, alphas, None)
                for bf in bs:
                    bf.molden_number = molden_number
                basis += bs

        stuff['basis'] = basis
                
        return True

    def read_orbitals(trigger_line):
        if not "[MO]" in trigger_line:
            return False
        
        assert(stuff['basis'] is not None)
        nbasis = len(stuff['basis'])

        orbitals = []
        energies = []
        spins = []
        occs = []
        names = []
        # Loop over basis functions
        while True:
            line = f.readline()
            linebuf.append(line)
            if "[" in line or not line:
                break
            linebuf.pop()

            if len(line.split()) == 0:
                continue

            names.append(line.split()[-1])
            energies.append(float(f.readline().split()[-1]))
            spins.append(f.readline().split()[-1])
            occs.append(float(f.readline().split()[-1]))
            
            orb = numpy.zeros(nbasis)
            for i in range(nbasis):
                #XXX: assuming no numbering monkey business
                orb[i] = float(f.readline().split()[1])

            orbitals.append(orb)


        stuff['orbitals'] = orbitals
        stuff['orbital_energies'] = energies
        stuff['orbital_spins'] = spins
        stuff['orbital_occs'] = occs
        stuff['orbital_names'] = names
                
        return True



    allparsers = [read_geo, read_basis, read_orbitals]
    while True: #parsing loop
        try:
            line = linebuf.pop()
        except IndexError:
            line = f.readline()
        if not line or line.startswith('@@@'):
            break

        for parse in allparsers:
            if parse(line):
                break


    # TODO: if we have a basis and a geometry, link them up
    if stuff['basis'] is not None and stuff['geo'] is not None:
        mn_to_atom = {}
        for atom in stuff['geo'].get_atoms():
            mn_to_atom[atom.molden_number] = atom

        for bf in stuff['basis']:
            bf.atom = mn_to_atom[bf.molden_number]


    if not washandle: f.close()

    return stuff

    


