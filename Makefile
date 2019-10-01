
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
	TRANSONIC_BACKEND="python" coverage run -p -m pytest transonic data_tests/ipynb
	TRANSONIC_BACKEND="numba" coverage run -p -m pytest transonic
	coverage run -p -m pytest transonic data_tests/ipynb

tests_coverage: tests_coverage_short
	TRANSONIC_BACKEND="cython" coverage run -p -m pytest transonic
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
