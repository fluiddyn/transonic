
COV=pytest --cov --cov-config=setup.cfg

develop:
	pip install -e lib/.
	pip install -e .[dev]

black:
	black -l 82 src lib data_tests tests

tests_pythran:
	TRANSONIC_BACKEND="pythran" pytest --nbval-lax tests data_tests/ipynb

tests_cython:
	TRANSONIC_BACKEND="cython" pytest tests data_tests/ipynb

tests_numba:
	TRANSONIC_BACKEND="numba" pytest tests data_tests/ipynb

tests_python:
	TRANSONIC_BACKEND="python" pytest tests data_tests/ipynb

tests_mpi:
	mpirun -np 2 pytest tests

tests_nbval:
	pytest --nbval data_tests/ipynb

tests_cov:
	mkdir -p .coverage
	pytest tests --cov-config setup.cfg

clean:
	rm -rf $(HOME)/.transonic/*/*/_transonic_testing/
	rm -rf $(HOME)/.transonic/*/*/*/_transonic_testing/
	rm -rf .coverage build dist

tests_coverage_short:
	mkdir -p .coverage
	COVERAGE_FILE=.coverage/coverage.python TRANSONIC_BACKEND="python" $(COV) tests
	COVERAGE_FILE=.coverage/coverage.numba TRANSONIC_BACKEND="numba" $(COV) tests
	COVERAGE_FILE=.coverage/coverage.pythran $(COV) tests

tests_ipynb:
	TRANSONIC_BACKEND="python" pytest --nbval-lax data_tests/ipynb
	pytest --nbval-lax data_tests/ipynb

tests_coverage_mpi:
	mpirun -np 2 coverage run --rcfile=setup.cfg -m mpi4py -m pytest tests

tests_coverage: tests_coverage_short tests_coverage_mpi
	COVERAGE_FILE=.coverage/coverage.cython TRANSONIC_BACKEND="cython" $(COV) tests

report_coverage:
	coverage combine
	coverage report
	coverage html
	coverage xml
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/index.html"

coverage_short: tests_coverage_short report_coverage
coverage: tests_coverage report_coverage
