tmp = float

T = tmp
T1 = int

const = 1
const_ann = 1


def func():
    i: T
    i = const
    ii: T1 = const_ann
    return i * ii
