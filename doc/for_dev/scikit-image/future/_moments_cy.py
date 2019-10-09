import numpy as np

from transonic import boost, Array


@boost(wraparound=False, cdivision=True, nonecheck=False)
def moments_hu(nu: "float64[:,:]"):
    hu: Array[np.float64, "1d", "C"] = np.zeros((7,), dtype=np.float64)
    t0: np.float64 = nu[3, 0] + nu[1, 2]
    t1: np.float64 = nu[2, 1] + nu[0, 3]
    q0: np.float64 = t0 * t0
    q1: np.float64 = t1 * t1
    n4: np.float64 = 4 * nu[1, 1]
    s: np.float64 = nu[2, 0] + nu[0, 2]
    d: np.float64 = nu[2, 0] - nu[0, 2]
    hu[0] = s
    hu[1] = d * d + n4 * nu[1, 1]
    hu[3] = q0 + q1
    hu[5] = d * (q0 - q1) + n4 * t0 * t1
    t0 *= q0 - 3 * q1
    t1 *= 3 * q0 - q1
    q0 = nu[3, 0] - 3 * nu[1, 2]
    q1 = 3 * nu[2, 1] - nu[0, 3]
    hu[2] = q0 * q0 + q1 * q1
    hu[4] = q0 * t0 + q1 * t1
    hu[6] = q1 * t0 - q0 * t1
    return np.asarray(hu)
