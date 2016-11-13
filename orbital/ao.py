import numpy

# generate a shell in the order expected by molden
def make_shell(shell,cs,alphas,atom):
    if shell == 's':
        return [AtomicOrbital(shell, 's', cs, alphas, atom)]

    elif shell == 'p':
        aos = []
        aos.append(AtomicOrbital(shell, 'px', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'py', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'pz', cs, alphas, atom))
        return aos

    elif shell == 'd':
        aos = []
        aos.append(AtomicOrbital(shell, 'dxx', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'dyy', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'dzz', cs, alphas, atom))

        aos.append(AtomicOrbital(shell, 'dxy', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'dxz', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'dyz', cs, alphas, atom))
        return aos

    elif shell == 'f':
        aos = []
        aos.append(AtomicOrbital(shell, 'fxxx', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'fyyy', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'fzzz', cs, alphas, atom))

        aos.append(AtomicOrbital(shell, 'fxyy', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'fxxy', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'fxxz', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'fxzz', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'fyzz', cs, alphas, atom))
        aos.append(AtomicOrbital(shell, 'fyyz', cs, alphas, atom))

        aos.append(AtomicOrbital(shell, 'fxyz', cs, alphas, atom))
        return aos

    else:
        raise NotImplementedError()

class AtomicOrbital:
    def __init__(s, shell, angular, cs, alphas, atom):
        s.shell = shell
        s.angular = angular
        
        # purge contraction gaussians with zero weight
        # (why does molpro output these things?!)
        trim_alphas = []
        trim_cs = []
        for i in range(len(alphas)):
            if numpy.abs(cs[i]) > 1e-14:
                trim_alphas.append(alphas[i])
                trim_cs.append(cs[i])

        s.alphas = numpy.array(trim_alphas)
        s.cs = numpy.array(trim_cs)
        s.atom = atom

        s.ncontract = len(s.alphas)
        assert(s.ncontract == len(s.cs))

        s._normalize()

    def f(s,x,y,z):
        ang_to_bohr = 1.889725989

        x0,y0,z0 = s.atom.r
        r = (x-x0)**2 + (y-y0)**2 + (z-z0)**2
        r *= ang_to_bohr**2
        expargs = numpy.exp(-r*s.alphas)
        vals = expargs * s.norms * s.cs 

        svals = vals.sum()

        if s.angular == 's':
            pass

        elif s.angular == 'px':
            svals *= x
        elif s.angular == 'py':
            svals *= y
        elif s.angular == 'pz':
            svals *= z

        elif s.angular == 'dxx':
            svals *= x*x
        elif s.angular == 'dyy':
            svals *= y*y
        elif s.angular == 'dzz':
            svals *= z*z
        elif s.angular == 'dxy':
            svals *= x*y
        elif s.angular == 'dxz':
            svals *= x*z
        elif s.angular == 'dyz':
            svals *= y*z

        elif s.angular == 'fxxx':
            svals *= x*x*x
        elif s.angular == 'fyyy':
            svals *= y*y*y
        elif s.angular == 'fzzz':
            svals *= z*z*z
        elif s.angular == 'fxyy':
            svals *= x*y*y
        elif s.angular == 'fxxy':
            svals *= x*x*y
        elif s.angular == 'fxxz':
            svals *= x*x*z
        elif s.angular == 'fxzz':
            svals *= x*z*z
        elif s.angular == 'fyzz':
            svals *= y*z*z
        elif s.angular == 'fyyz':
            svals *= y*y*z
        elif s.angular == 'fxyz':
            svals *= x*y*z

        else:
            raise NotImplementedError()
        
        return svals


    def _normalize(s):
        s.norms = numpy.ones(s.ncontract)

        p = (2/numpy.pi)**0.75


        apowers = {
            's': 0.75,
            'p': 1.25,
            'd': 1.75,
            'f': 2.25
            }

        prefactors = {
            's': 1.0,

            'px': 2.0,
            'py': 2.0,
            'pz': 2.0,

            #'dxx': 4/numpy.sqrt(3),
            #'dyy': 4/numpy.sqrt(3),
            #'dzz': 4/numpy.sqrt(3),
            #'dxy': 4.0,
            #'dxz': 4.0,
            #'dyz': 4.0,

            'dxx': 4,
            'dyy': 4,
            'dzz': 4,
            'dxy': 4.0*numpy.sqrt(3),
            'dxz': 4.0*numpy.sqrt(3),
            'dyz': 4.0*numpy.sqrt(3),

            #'fxxx': 8/numpy.sqrt(15),
            #'fyyy': 8/numpy.sqrt(15),
            #'fzzz': 8/numpy.sqrt(15),
            #'fxyy': 8/numpy.sqrt(3),
            #'fxxy': 8/numpy.sqrt(3),
            #'fxxz': 8/numpy.sqrt(3),
            #'fxzz': 8/numpy.sqrt(3),
            #'fyzz': 8/numpy.sqrt(3),
            #'fyyz': 8/numpy.sqrt(3),
            #'fxyz': 8.0

            'fxxx': 8,
            'fyyy': 8,
            'fzzz': 8,
            'fxyy': 8*numpy.sqrt(5),
            'fxxy': 8*numpy.sqrt(5),
            'fxxz': 8*numpy.sqrt(5),
            'fxzz': 8*numpy.sqrt(5),
            'fyzz': 8*numpy.sqrt(5),
            'fyyz': 8*numpy.sqrt(5),
            'fxyz': 8*numpy.sqrt(15)
            }
        s.norms *= p * prefactors[s.angular]

        for i in range(s.ncontract):
            alpha = s.alphas[i]
            s.norms[i] *= alpha ** apowers[s.shell]









