
develop:
	python setup.py develop

black:
	black -l 82 fluidpythran

tests:
	pytest -s
