
CLANG=clang-6.0
CXXLANG=clang++-6.0

all:
	python setup_pyx.py
	python setup.py

all_clang:
	CXX=$(CXXLANG) CC=$(CLANG) python setup_pyx.py
	CXX=$(CXXLANG) CC=$(CLANG) python setup.py

clean_all:
	rm -f pyx/*.so pyx/*.html pyx/*.c
	rm -rf future/__pythran__ future/__cython__ future/__numba__
