from transonic import boost
import numpy as np



@boost
def primes(nb_primes : int, a : int= 1, b = None):
    n : int 
    len_p : int
    i : int
    p = np.zeros(1000)
    
    if nb_primes > 1000:
        nb_primes = 1000

    len_p = 2  # The current number of elements in p.
    n = 2
    while len_p < nb_primes:
        # Is n prime?
        for i in p[:len_p]:
            if n % i == 0:
                break

        # If no break occurred in the loop, we have a prime.
        else:
            p[len_p] = n
            len_p += 1
        n += 1

    # Let's return the result in a python list:
    result_as_list  = [prime for prime in p[:len_p]]
    return result_as_list

print(primes(10))
