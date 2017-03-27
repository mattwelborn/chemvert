import chemvert

stuff = chemvert.io.molpro.load_output("0308.out")
print stuff['energies']
print stuff['mulliken_pops']
print stuff['ibba_pops']
