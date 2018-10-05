
develop:
	python setup.py develop

black:
	black -l 82 fluidpythran

tests:
	pytest fluidpythran

tests_coverage:
	mkdir -p .coverage
	coverage run -p -m pytest

report_coverage:
	coverage combine
	coverage report
	coverage html
	coverage xml
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/index.html"

coverage: tests_coverage report_coverage
