
develop:
	pip install -e .[test]

black:
	black -l 82 fluidpythran fluidpythran_cl

tests:
	pytest fluidpythran data_tests/ipynb

tests_mpi:
	mpirun -np 2 pytest fluidpythran

tests_nbval:
	pytest --nbval data_tests/ipynb

clean:
	rm -rf $(HOME)/.fluidpythran/__cachedjit__/fluidpythran/
	rm -rf $(HOME)/.fluidpythran/__cachedjit_classes__/fluidpythran/
	rm -rf $(HOME)/.fluidpythran/__cachedjit__/__cachedjit_classes__/fluidpythran/
	rm -rf fluidpythran/__pythran__/

tests_coverage:
	mkdir -p .coverage
	coverage run -p -m pytest
	mpirun -np 2 coverage run -p -m pytest fluidpythran

report_coverage:
	coverage combine
	coverage report
	coverage html
	coverage xml
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/index.html"

coverage: tests_coverage report_coverage
