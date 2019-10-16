from subprocess import getoutput
import sys

decorator = "boost"
if "jit" in sys.argv:
    decorator = "jit"

print(f"With decorator {decorator}:")


def get_times(backend):
    output = getoutput(
        f"TRANSONIC_BACKEND='{backend}' python row_sum_{decorator}.py"
    )
    lines = output.split("\n")
    index_backend = 1
    if decorator == "jit":
        index_backend = 2
    assert lines[index_backend] == backend.capitalize()
    time_high = float(lines[index_backend + 1].split()[1])
    time_low = float(lines[index_backend + 2].split()[1])
    return time_high, time_low


backend = "python"
time_high, time_low = get_times(backend)

time_ref = time_high


def print_result(backend, time_high, time_low):
    print(backend.capitalize())
    print(f"high level: {time_high:.2e} s  (= {time_high/time_ref:5.2f} * norm)")
    print(f"low level:  {time_low:.2e} s  (= {time_low/time_ref:5.2f} * norm)\n")


print_result(backend, time_high, time_low)

for backend in ("cython", "numba", "pythran"):
    time_high, time_low = get_times(backend)
    print_result(backend, time_high, time_low)
