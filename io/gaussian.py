import common
from ..matter import geometry,periodic_table

import os
import numpy

def load_output(fl,nowarn=False):
    f, washandle = common.get_file_read_handle(fl)
    stuff = {}
    stuff['done'] = False
    stuff['geos'] = []
    stuff['charge'] = None
    stuff['spin'] = None

    def read_done(trigger_line):
        if not "Normal termination of Gaussian" in trigger_line:
            return False
        stuff['done'] = True
        return True

    def read_geos(trigger_line):
        if not "Standard orientation" in trigger_line:
            return False
        f.readline()
        f.readline()
        f.readline()
        f.readline()

        geo = geometry.Geometry()
        while True:
            line = f.readline()
            if '------------------' in line:
                break

            s = line.split()
            number = int(s[1])
            a = periodic_table.by_number(number)
            if not a:
                a = atom.Atom(None, None, number, None, None)

            r = numpy.array(map(float, s[3:6]))
            a.r = r
            geo.append(a)

        stuff['geos'].append(geo)
        return True

    def read_charge_spin(trigger_line):
        if not ("Charge =" in trigger_line and "Multiplicity =" in trigger_line):
            return False
        s = trigger_line.split()
        stuff['charge'] = int(s[2])
        stuff['spin']   = int(s[5])
        return True

    


    allparsers = [read_done, read_geos, read_charge_spin]
    while True: #parsing loop
        line = f.readline()
        if not line or line.startswith('@@@'):
            break

        for parse in allparsers:
            if parse(line):
                break

    if not washandle: f.close()

    return stuff

    


