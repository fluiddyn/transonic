NAME=proj.py

all: pythran cython other

pythran:
	transonic $(NAME) -b pythran -pf "-DUSE_XSIMD -Ofast"

cython:
	transonic $(NAME) -b cython -pf "-Ofast "

other:
	transonic $(NAME) -b numba
	transonic $(NAME) -b python

clean:
	rm -rf __cython__ __python__ __numba__ __pythran__

bench:
	python proj.py
