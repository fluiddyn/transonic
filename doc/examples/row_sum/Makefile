NAME=row_sum_boost.py
NAMEJIT=row_sum_jit.py


all: pythran cython other

pythran:
	transonic $(NAME) -b pythran -pf "-march=native -DUSE_XSIMD -Ofast"

cython:
	transonic $(NAME) -b cython -pf "-march=native -Ofast"

other:
	transonic $(NAME) -b numba
	transonic $(NAME) -b python

clean:
	rm -rf __cython__ __python__ __numba__ __pythran__

bench:
	python bench.py

bench_cython:
	TRANSONIC_BACKEND="cython" python $(NAME)

bench_numba:
	TRANSONIC_BACKEND="numba" python $(NAME)

bench_pythran:
	TRANSONIC_BACKEND="pythran" python $(NAME)

bench_python:
	TRANSONIC_BACKEND="python" python $(NAME)

bench_jit:
	python bench.py jit