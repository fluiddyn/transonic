import numpy as np

from transonic.util import print_versions, timeit_verbose

from mod_pythran import fxfy as fxfy_pythran, fxfy_loops as fxfy_loops_pythran


def fxfy(ft, fn, theta):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    fx = (cos_theta * ft) - (sin_theta * fn)
    fy = (sin_theta * ft) + (cos_theta * fn)
    return fx, fy


theta = np.linspace(0, 2 * np.pi, 10000)
ft = 2.5 * theta
fv = 1.5 * theta

print_versions()

loc = locals()

norm = timeit_verbose("fxfy(ft, fv, theta)", globals=loc)
timeit_verbose("fxfy_pythran(ft, fv, theta)", globals=loc, norm=norm)
timeit_verbose("fxfy_loops_pythran(ft, fv, theta)", globals=loc, norm=norm)
