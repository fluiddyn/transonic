from transonic import jit
from for_test_exterior_import_jit import fib


fib_jitted = jit(fib)




if __name__ == "__main__":

    fib_jitted(1)
    