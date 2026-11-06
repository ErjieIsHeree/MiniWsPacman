SRC:=./src
MAIN:=./pac-man.py
CONFIG:=./config.json


install:
	uv sync

uvr:
	uv run $(MAIN) $(CONFIG)

run:
	python3 $(MAIN) $(CONFIG)

debug: 
	python3 -m pdb $(MAIN) $(CONFIG)

clean:
	find $(SRC) \( -name "__pycache__" -o -name ".mypy_cache" \) -prune -exec rm -rf {} +

lint: 
	python3 -m flake8 $(SRC) & python3 -m mypy $(SRC) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	python3 -m flake8 $(SRC) & python3 -m mypy $(SRC) --strict
