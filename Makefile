
COV=pytest --cov=transonic --cov-append --cov-config=setup.cfg --no-cov

develop:
	pip install -e .[dev]

black:
	black -l 82 transonic transonic_cl data_tests

tests:
	pytest --nbval-lax transonic data_tests/ipynb

tests_cython:
	TRANSONIC_BACKEND="cython" pytest transonic data_tests/ipynb

tests_numba:
	TRANSONIC_BACKEND="numba" pytest transonic data_tests/ipynb

tests_python:
	TRANSONIC_BACKEND="python" pytest transonic data_tests/ipynb

tests_mpi:
	mpirun -np 2 pytest transonic

tests_nbval:
	pytest --nbval data_tests/ipynb

tests_cov:
	mkdir -p .coverage
	pytest --cov-config setup.cfg --cov=transonic

clean:
	rm -rf $(HOME)/.transonic/*/*/_transonic_testing/
	rm -rf $(HOME)/.transonic/*/*/*/_transonic_testing/
	rm -rf .coverage build dist

tests_coverage_short:
	mkdir -p .coverage
	TRANSONIC_BACKEND="python" $(COV) --nbval-lax transonic data_tests/ipynb
	TRANSONIC_BACKEND="numba" $(COV) transonic
	$(COV) --nbval-lax transonic data_tests/ipynb

tests_coverage: tests_coverage_short
	TRANSONIC_BACKEND="cython" $(COV) transonic
	mpirun -np 2 $(COV) transonic

report_coverage:
	coverage combine
	coverage report
	coverage html
	coverage xml
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/index.html"

coverage_short: tests_coverage_short report_coverage
coverage: tests_coverage report_coverage
