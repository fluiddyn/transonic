
develop:
	pip install -e .[test]

black:
	black -l 82 transonic transonic_cl

tests:
	pytest transonic data_tests/ipynb

tests_mpi:
	mpirun -np 2 pytest transonic

tests_nbval:
	pytest --nbval data_tests/ipynb

clean:
	rm -rf $(HOME)/.transonic/__jit__/transonic/
	rm -rf $(HOME)/.transonic/__jit_classes__/transonic/
	rm -rf $(HOME)/.transonic/__jit__/__jit_classes__/transonic/
	rm -rf transonic/__pythran__/

tests_coverage:
	mkdir -p .coverage
	coverage run -p -m pytest
	mpirun -np 2 coverage run -p -m pytest transonic

report_coverage:
	coverage combine
	coverage report
	coverage html
	coverage xml
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/index.html"

coverage: tests_coverage report_coverage
