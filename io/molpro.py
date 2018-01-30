import numpy

import common
from .. import constants


def load_output(fl, nowarn=False):
    f, washandle = common.get_file_read_handle(fl)
    stuff = {}
    stuff['done'] = False
    stuff['active_mos'] = None
    stuff['energies'] = []
    stuff['gaps'] = []
    stuff['HOMOs'] = []
    stuff['LUMOs'] = []
    stuff['orb_energies'] = []
    stuff['natorbs'] = []
    stuff['mulliken_pops'] = []
    stuff['ibba_pops'] = []
    stuff['T1s'] = []

    def read_vmr(trigger_line):
        if not " Variable memory released" in trigger_line:
            return False
        stuff['done'] = True
        return True

    def read_active_mos(trigger_line):
        if "MOs in active region:" not in trigger_line:
            return False
        stuff['active_mos'] = trigger_line.split()[4:]
        while True:
            line = f.readline()
            s = line.split()
            if len(s) == 0:
                break
            stuff['active_mos'] += s

        return True

    def read_rks_energy(trigger_line):
        if "!RKS STATE" not in trigger_line or "Energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'RKS', 'energy': e})

        return True

    def read_rhf_energy(trigger_line):
        if "!RHF STATE" not in trigger_line or "Energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'RHF', 'energy': e})

        return True

    def read_embed_popmat(trigger_line):
        if "BEGIN EMBEDDING POP MATRIX" not in trigger_line:
            return False
        ncen, nlmo = map(int, f.readline().split())
        f.readline()
        f.readline()

        M = numpy.zeros((ncen,nlmo))
        pos = 0
        while True:
            width = len(f.readline().split())
            for i in range(ncen):
                line = f.readline()
                vals = numpy.array(map(float, line.split()[1:]))
                M[i,pos:pos+width] = vals
            pos += width
            if pos == nlmo:
                break
        stuff['embed_popmat'] = M
        return True


    # TODO: MP2 and CC energies and stuff
    def read_ccsdt_energy(trigger_line):
        if "!CCSD(T) total energy:" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'CCSD(T)', 'energy': e})

        return True

    def read_reference_energy(trigger_line):
        if "Reference energy: " not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'Ref', 'energy': e})

        return True

    def read_ccsd_correlation_energy(trigger_line):
        if "CCSD correlation energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'CCSD corr', 'energy': e})

        return True

    def read_ccsd_energy(trigger_line):
        if "!CCSD total energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'CCSD', 'energy': e})

        return True

    def read_dcsd_energy(trigger_line):
        if "!DCSD total energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'DCSD', 'energy': e})

        return True

    def read_bccd_energy(trigger_line):
        if "!BCCD total energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'BCCD', 'energy': e})

        return True

    def read_rmp2_energy(trigger_line):
        if "!RMP2 STATE" not in trigger_line or "Energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'RMP2', 'energy': e})

        return True

    def read_ump2_energy(trigger_line):
        if "!UMP2 STATE" not in trigger_line or "Energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'UMP2', 'energy': e})

        return True

    def read_lmp2_energy(trigger_line):
        if "!LMP2 total energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'LMP2', 'energy': e})

        return True

    def read_natorbs(trigger_line):
        if "Natural orbitals" not in trigger_line or "saved on record" in trigger_line:
            return False

        natorbs = []
        while True:
            line = f.readline()

            if "Electronic charge" in line:
                break

            front = line[:21]
            s = front.split()
            if len(s) != 2:
                continue
            try:
                pop = float(s[1])
                orb = s[0]
                s = line.split()
                coeff = map(float, s[2:])
                while True:
                    line = f.readline()
                    s = line.split()
                    if len(s) == 0:
                        break
                    coeff += map(float, s)

                natorbs.append([orb,pop,numpy.array(coeff)])
            except(ValueError):
                continue

        stuff['natorbs'].append(natorbs)
        return True

    def read_T1_diagnostic(trigger_line):
        if "T1 diagnostic:" not in trigger_line:
            return False

        stuff['T1s'].append(float(trigger_line.split()[-1]))
        return True

    def read_orbital_energies(trigger_line):
        if "ELECTRON ORBITALS" not in trigger_line:
            return False

        energies = []
        while True:
            line = f.readline()
            if " HOMO " in line:
                break

            front = line[:31]
            s = front.split()
            if len(s) != 4:
                continue
            try:
                en = float(s[2])
                energies.append(en)
            except(ValueError):
                continue

        stuff['orb_energies'].append(numpy.array(energies))
        s = line.split()
        energy = float(s[-1].rstrip('eV')) *  constants.ev_to_hartree
        name = s[1]
        number = int(name.split('.')[0])
        homo = {'energy': energy, 'name': name, 'number': number}
        stuff['HOMOs'].append(homo)

        line = f.readline()
        s = line.split()
        energy = float(s[-1].rstrip('eV')) *  constants.ev_to_hartree
        name = s[1]
        number = int(name.split('.')[0])
        lumo = {'energy': energy, 'name': name, 'number': number}
        stuff['LUMOs'].append(lumo)

        line = f.readline()
        s = line.split()
        gap = float(s[-1].rstrip('eV')) *  constants.ev_to_hartree
        stuff['gaps'].append(gap)

        return True
        return True

    def read_ibba(trigger_line):
        if "Total charge composition:" not in trigger_line:
            return False

        f.readline()
        if "CEN ATOM" not in f.readline():
            return False

        charges = []
        while True:
            line = f.readline()
            s = line.split()
            if not line or len(s)==0:
                break
            charge = float(s[-1])
            charges.append(charge)
        stuff['ibba_pops'].append(numpy.array(charges))


        return True

    def find_ibba_deloc(trigger_line):
        if "Summary of localized orbital composition: " not in trigger_line:
            return False

        f.readline()
        if "ORB.ENERGY" not in f.readline():
            return False

        delocs = []
        while True:
            line = f.readline()
            s = line.split()
            if not line or len(s)==0:
                break
            if len(s) > 11:
                delocs.append(int(s[0]))

        stuff['ibba_delocs'] = delocs
        return True


    def read_mulliken(trigger_line):
        if "Population analysis by basis function type" not in trigger_line:
            return False

        f.readline()
        if "Unique atom" not in f.readline():
            return False

        charges = []
        while True:
            line = f.readline()
            s = line.split()
            if not line or len(s) == 0:
                break
            sign = s[8]
            charge = float(s[9])
            if sign == '-':
                charge *= -1
            charges.append(charge)
        stuff['mulliken_pops'].append(numpy.array(charges))
        return True




    allparsers = [read_vmr, read_active_mos, read_rks_energy, read_rhf_energy, read_lmp2_energy, read_rmp2_energy, read_ump2_energy, read_orbital_energies, read_mulliken, read_ibba, find_ibba_deloc, read_embed_popmat, read_natorbs, read_ccsdt_energy, read_ccsd_energy, read_bccd_energy, read_dcsd_energy, read_T1_diagnostic, read_ccsd_correlation_energy, read_reference_energy]
    while True: #parsing loop
        line = f.readline()
        if not line or line.startswith('@@@'):
            break

        for parse in allparsers:
            if parse(line):
                break

    if not washandle: f.close()

    return stuff




