import common
from ..matter import geometry

class QChemOptions:
    def __init__(self, charge=0, spin=1, rem={'basis':'sto-3g', 'exchange':'hf'}):
        self.charge = charge
        self.spin   = spin
        self.rem    = rem
    def rem_str(self):
        ret = ""
        for key in self.rem:
            ret += "%s %s\n" % (key, self.rem[key])
        return ret
            

def load(f):
    f, washandle = common.get_file_read_handle(f)

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


def save(f, geo, options, rename = {}, delete = []):
    f, washandle = common.get_file_write_handle(f)

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

    if not washandle: f.close()
