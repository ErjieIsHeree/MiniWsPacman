SRC:=./src


install:
	

run:
	

debug: 
	

clean:
	find $(SRC) \( -name "__pycache__" -o -name ".mypy_cache" \) -prune -exec rm -rf {} +

lint: 
	python3 -m flake8 $(SRC) & python3 -m mypy $(SRC) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	python3 -m flake8 $(SRC) & python3 -m mypy $(SRC) --strict
