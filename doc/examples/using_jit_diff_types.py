from transonic import jit, Type

T = Type(int, float)

@jit()
def func(a: T, b: T):
    return a * b

if __name__ == "__main__":

    from time import sleep

    a_i = b_i = 1
    a_f = b_f = 1.

    for _ in range(10):
        print(_, end=",", flush=True)
        func(a_i, b_i)
        sleep(1)

    print()

    for _ in range(10):
        print(_, end=",", flush=True)
        func(a_f, b_f)
        sleep(1)
