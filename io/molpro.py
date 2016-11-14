import common
from ..matter import geometry,periodic_table

import os
import numpy

def load_output(fl,nowarn=False):
    f, washandle = common.get_file_read_handle(fl)
    stuff = {}
    stuff['done'] = False
    stuff['active_mos'] = None

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




    allparsers = [read_vmr, read_active_mos]
    while True: #parsing loop
        line = f.readline()
        if not line or line.startswith('@@@'):
            break

        for parse in allparsers:
            if parse(line):
                break

    if not washandle: f.close()

    return stuff

    


