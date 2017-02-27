import common
from ..matter import geometry,periodic_table

import os
import numpy

def load_output(fl,nowarn=False):
    f, washandle = common.get_file_read_handle(fl)
    stuff = {}
    stuff['done'] = False
    stuff['active_mos'] = None
    stuff['energies'] = []
    stuff['gaps'] = []

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



    def read_gap(trigger_line):
        if "LUMO-HOMO" not in trigger_line:
            return False
        
        s = line.split()
        gap = float(s[-1])
        stuff['gaps'].append(gap)


    # TODO: MP2 and CC energies and stuff
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






    allparsers = [read_vmr, read_active_mos, read_rks_energy, read_rhf_energy, read_lmp2_energy, read_rmp2_energy, read_ump2_energy, read_gap]
    while True: #parsing loop
        line = f.readline()
        if not line or line.startswith('@@@'):
            break

        for parse in allparsers:
            if parse(line):
                break

    if not washandle: f.close()

    return stuff

    


