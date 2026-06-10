install:

run:

debug:

clean:

lint: flake8 .  mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs\
--check-untyped-defs

lint-strict: