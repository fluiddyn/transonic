
all:
	transonic -b pythran add.py
	transonic -b numba add.py
	transonic -b cython add.py

bench:
	TRANSONIC_NO_REPLACE=1 python add.py
	TRANSONIC_BACKEND="pythran" python add.py
	TRANSONIC_BACKEND="numba" python add.py
	TRANSONIC_BACKEND="cython" python add.py

clean:
	rm -rf __pythran__ __cython__ __numba__