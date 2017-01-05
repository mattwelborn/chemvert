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

    def read_vmr(trigger_line):
        if not " Variable memory released" in trigger_line:
            return False
        stuff['done'] = True
        return True
    
    def read_active_mos(trigger_line):
        if "MOs in active region:" not in trigger_line:
            return False
        stuff['active_mos'] = trigger_line.split()[4:]

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


    # TODO: MP2 and CC energies and stuff




    allparsers = [read_vmr, read_active_mos, read_rks_energy, read_rhf_energy]
    while True: #parsing loop
        line = f.readline()
        if not line or line.startswith('@@@'):
            break

        for parse in allparsers:
            if parse(line):
                break

    if not washandle: f.close()

    return stuff

    


