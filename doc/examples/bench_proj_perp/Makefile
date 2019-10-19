NAME=bench.py

all: pythran cython other

pythran:
	transonic $(NAME) -b pythran -af "-march=native -DUSE_XSIMD -Ofast"

cython:
	transonic $(NAME) -b cython -af "-march=native -Ofast"

other:
	transonic $(NAME) -b numba
	transonic $(NAME) -b python

clean:
	rm -rf __cython__ __python__ __numba__ __pythran__

bench:
	python $(NAME)
