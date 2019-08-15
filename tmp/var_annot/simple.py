from transonic import boost

tmp = float

T = tmp
T1 = int
T2 = float

const = 1
const_ann = 1

@boost
def func(a: T2):
    i: T
    i = const
    ii: T1 = const_ann
    return i * ii * a
