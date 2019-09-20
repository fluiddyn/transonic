
NAME=bench_aot.py

all: pythran cython other

pythran:
	transonic -b pythran $(NAME) -pf "-march=native -DUSE_XSIMD"

cython:
	transonic -b cython $(NAME)

other:
	transonic -b python $(NAME)
	transonic -b numba $(NAME)

clean:
	rm -rf __cython__ __python__ __numba__ __pythran__

bench:
	python bench_aot.py

bench_jit:
	python bench_jit.py