bench:
	rm -rf mod_pythran.*.so
	pythran mod_pythran.py -DUSE_XSIMD -Ofast -march=native
	python bench.py
