
clean:
	rm -rf __cython__ __numba__ __pythran__ __python__ __jax__

all:
	transonic -b pythran -nc *.py
	transonic -b python -nc *.py
	transonic -b cython -nc *.py
	transonic -b numba -nc *.py
	transonic -b jax -nc *.py

meld_pythran:
	meld __pythran__ saved__backend__/pythran

meld_python:
	meld __python__ saved__backend__/python

meld_cython:
	meld __cython__ saved__backend__/cython

meld_numba:
	meld __numba__ saved__backend__/numba

meld_jax:
	meld __jax__ saved__backend__/jax

saved__backend__/%: __%__ FORCE
	rsync -aP $< $@

rsync: saved__backend__/pythran saved__backend__/python saved__backend__/cython saved__backend__/numba

FORCE:
