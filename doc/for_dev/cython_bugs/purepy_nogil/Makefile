all:
	python -m transonic_cl.cythonize simple.pyx
	python -m transonic_cl.cythonize pure_wo_pxd.py
	python -m transonic_cl.cythonize pure_wo_pxd_ccall.py
	python -m transonic_cl.cythonize pure_with_pxd.py

clean:
	rm -f *.c *.cpython-37m-x86_64-linux-gnu.so
	rm -rf build __pycache__

try:
	python -c "import simple as m; print(m.use_add(10))"
	python -c "import pure_wo_pxd as m; print(m.use_add(10))"
	python -c "import pure_with_pxd as m; print(m.use_add(10))"
