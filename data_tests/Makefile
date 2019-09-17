
clean:
	rm -rf __cython__ __numba__ __pythran__ __python__

all:
	TRANSONIC_BACKEND="pythran" transonic -np *.py
	TRANSONIC_BACKEND="python" transonic -np *.py
	TRANSONIC_BACKEND="cython" transonic -np *.py
	TRANSONIC_BACKEND="numba" transonic -np *.py

meld_pythran:
	meld __pythran__ saved__backend__/pythran

meld_python:
	meld __python__ saved__backend__/python

meld_cython:
	meld __cython__ saved__backend__/cython

meld_numba:
	meld __numba__ saved__backend__/numba
