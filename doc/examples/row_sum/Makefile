NAME=row_sum_boost.py
NAMEJIT=row_sum_jit.py


all: pythran cython other

pythran:
	transonic $(NAME) -b pythran -pf "-march=native -DUSE_XSIMD"

cython:
	transonic $(NAME) -b cython

other:
	transonic $(NAME) -b numba
	transonic $(NAME) -b python

clean:
	rm -rf __cython__ __python__ __numba__ __pythran__

bench: bench_python bench_cython bench_numba bench_pythran

bench_cython:
	TRANSONIC_BACKEND="cython" python $(NAME)

bench_numba:
	TRANSONIC_BACKEND="numba" python $(NAME)

bench_pythran:
	TRANSONIC_BACKEND="pythran" python $(NAME)

bench_python:
	TRANSONIC_BACKEND="python" python $(NAME)

bench_jit:
	TRANSONIC_BACKEND="cython" python $(NAMEJIT)
	TRANSONIC_BACKEND="numba" python $(NAMEJIT)
	TRANSONIC_BACKEND="pythran" python $(NAMEJIT)