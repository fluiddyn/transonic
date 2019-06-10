# pythran export compute(complex128[:, :, :], complex128[:, :, :], complex128, complex128[:, :, :], str)
# pythran export compute(complex128[:, :, :], complex128[:, :, :], complex128, float32[:, :, :, :], str)
# pythran export compute(complex128[:, :, :], complex128[:, :, :], int, complex128[:, :, :], str)
# pythran export compute(complex128[:, :, :], complex128[:, :, :], int, float32[:, :, :, :], str)
# pythran export compute(complex128[:], complex128[:], complex128, complex128[:], str)
# pythran export compute(complex128[:], complex128[:], complex128, float32[:, :], str)
# pythran export compute(complex128[:], complex128[:], int, complex128[:], str)
# pythran export compute(complex128[:], complex128[:], int, float32[:, :], str)
# pythran export compute(int[:, :, :], int[:, :, :], complex128, float32[:, :, :, :], str)
# pythran export compute(int[:, :, :], int[:, :, :], complex128, int[:, :, :], str)
# pythran export compute(int[:, :, :], int[:, :, :], int, float32[:, :, :, :], str)
# pythran export compute(int[:, :, :], int[:, :, :], int, int[:, :, :], str)
# pythran export compute(int[:], int[:], complex128, float32[:, :], str)
# pythran export compute(int[:], int[:], complex128, int[:], str)
# pythran export compute(int[:], int[:], int, float32[:, :], str)
# pythran export compute(int[:], int[:], int, int[:], str)
def compute(a, b, c, d, e):
    print(e)
    tmp = a + b
    return (tmp > 1) and (tmp > 2)


# pythran export __transonic__
__transonic__ = ("0.2.2",)
