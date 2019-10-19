NAME=bench.py

all: pythran other

pythran:
	transonic $(NAME) -b pythran -af "-march=native -DUSE_XSIMD -Ofast"

other:
	transonic $(NAME) -b numba

clean:
	rm -rf __cython__ __python__ __numba__ __pythran__

bench:
	python bench.py
