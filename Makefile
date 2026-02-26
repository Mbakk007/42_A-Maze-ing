# File: Makefile

install:
	install:
	pip install --upgrade pip
	pip install flake8 mypy
	@echo "Dependencies installed: flake8, mypy"

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

clean:
	rm -rf __pycache__ .mypy_cache *.pyc *.pyo maze.txt

lint:
	flake8 . && mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . && mypy . --strict
