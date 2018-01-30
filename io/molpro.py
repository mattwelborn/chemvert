import numpy
import chemvert
import StringIO

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
    stuff['noconv'] = False
    stuff['nogeoconv'] = False
    stuff['scf_histories'] = []
    stuff['overlaps'] = []

    def read_vmr(trigger_line):
        if not " Variable memory released" in trigger_line:
            return False
        stuff['done'] = True
        return True

    def read_mct(trigger_line):
        if not "Molpro calculation terminated" in trigger_line:
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

    def read_scf_history(trigger_line):
        if "ITERATION   DDIFF            GRAD" not in trigger_line:
            return False

        history = []
        while True:
            line = f.readline()
            if "Final occupancy" in line:
                break
            if "Final alpha occupancy" in line:
                break
            it = {}
            try:
                if "Generated new metagrid" in line:
                    continue
                if "Computed new grid" in line:
                    continue
                it["energy"] = float(line.split()[3])
                history.append(it)
            except(IndexError):
                pass
            except(ValueError):
                print "read_scf_history choked on", line,
        stuff['scf_histories'].append(history)
        return True



    def read_overlap(trigger_line):
        if "Orbital overlap <old|new>" not in trigger_line:
            return False
        line = trigger_line.split(':')[1]


        overlaps = []
        while True:
            s = line.split('>=')[1:]
            #print line,
            for q in s:
                #print q
                overlaps.append(float(q.split()[0]))
            line = f.readline()
            if not line.strip().startswith('<'):
                break
        stuff['overlaps'].append(numpy.array(overlaps))
        return True

    def read_uks_energy(trigger_line):
        if "!UKS STATE" not in trigger_line or "Energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'UKS', 'energy': e})

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
        if "!CCSD(T) total energy" not in trigger_line:
            return False

        s = line.split()
        e = float(s[-1])
        stuff['energies'].append({'kind': 'CCSD(T)', 'energy': e})

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
            if "Orbital spaces for UNO-CAS" in line:
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

    def read_gap(trigger_line):
        if not "LUMO-HOMO" in trigger_line:
            return False
        s = trigger_line.split()
        gap = float(s[-1].rstrip('eV')) *  constants.ev_to_hartree
        stuff['gaps'].append(gap)

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
        orbs = []
        energies = []
        while True:
            line = f.readline()
            s = line.split()
            if not line or len(s)==0:
                break
            energies.append(float(s[2]))
            if len(s) > 11:
                delocs.append(int(s[0]))
            orb = []
            #for group in [line[n:n+15] for n in range(28, len(line), 15)]:
            ##for group in [s[n:n+3] for n in range(3, len(s), 3)]:
            #    if group[0:len(" (other:")] == " (other:":
            #        break
            #    #print group
            #    orb.append([group[0:2],int(group[2:5]),float(group[5:])])
            orbs.append(orb)

        stuff['ibba_delocs'] = delocs
        stuff['ibba_orbs'] = orbs
        stuff['ibba_energies'] = energies
        return True


    def read_no_conv(trigger_line):
        if "No convergence" in trigger_line and 'max' not in trigger_line:
            stuff['noconv'] = True
            return True
        else:
            return False

    def read_no_geo_conv(trigger_line):
        if "No convergence in max. number of iterations" in trigger_line:
            stuff['nogeoconv'] = True
            return True
        else:
            return False

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

    def read_end_geo(trigger_line):
        if "END OF GEOMETRY OPTIMIZATION." not in trigger_line:
            return False

        f.readline()
        if 'Current geometry' not in f.readline():
            return False

        f.readline()
        geo, extras = chemvert.io.xyz.load(f)
        stuff['end_geo'] = [geo, extras]
        return True

    def read_trunc_AOs(trigger_line):
        if "MGW printing truncation AOs" not in trigger_line:
            return False

        nao = int(f.readline().split('.')[0])
        f.readline()
        aos = [int(f.readline().split('.')[0]) for i in range(nao)]

        stuff['trunc_AOs'] = aos
        return True






    allparsers = [read_vmr, read_active_mos, read_rks_energy, read_rhf_energy, read_lmp2_energy, read_rmp2_energy, read_ump2_energy, read_orbital_energies, read_mulliken, read_ibba, find_ibba_deloc, read_embed_popmat, read_natorbs, read_ccsdt_energy, read_ccsd_energy, read_bccd_energy, read_dcsd_energy, read_gap, read_mct, read_uks_energy, read_no_conv,read_no_geo_conv,read_end_geo,read_trunc_AOs, read_scf_history, read_overlap]
    while True: #parsing loop
        line = f.readline()
        if not line or line.startswith('@@@'):
            break

        for parse in allparsers:
            if parse(line):
                break

    if not washandle: f.close()

    return stuff




