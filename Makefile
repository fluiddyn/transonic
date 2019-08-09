
develop:
	pip install -e .[dev]

black:
	black -l 82 transonic transonic_cl data_tests

tests:
	pytest transonic data_tests/ipynb

tests_cython:
	TRANSONIC_BACKEND="cython" pytest transonic data_tests/ipynb

tests_numba:
	TRANSONIC_BACKEND="numba" pytest transonic data_tests/ipynb

tests_mpi:
	mpirun -np 2 pytest transonic

tests_nbval:
	pytest --nbval data_tests/ipynb

tests_cov:
	mkdir -p .coverage
	pytest --cov-config setup.cfg --cov=transonic

clean:
	rm -rf $(HOME)/.transonic/__jit__/transonic/
	rm -rf $(HOME)/.transonic/__jit_classes__/transonic/
	rm -rf $(HOME)/.transonic/__jit__/__jit_classes__/transonic/
	rm -rf transonic/__pythran__/

tests_coverage_short:
	mkdir -p .coverage
	coverage run -p -m pytest

tests_coverage: tests_coverage_short
	TRANSONIC_BACKEND="cython" coverage run -p -m pytest
	mpirun -np 2 coverage run -p -m pytest transonic

report_coverage:
	coverage combine
	coverage report
	coverage html
	coverage xml
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/index.html"

coverage_short: tests_coverage_short report_coverage
coverage: tests_coverage report_coverage
