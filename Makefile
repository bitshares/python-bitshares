.PHONY: clean
clean: clean-build clean-pyc

.PHONY: clean-build
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__/ .eggs/ .cache/
	rm -rf .tox/ .pytest_cache/ .benchmarks/

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

.PHONY: lint
lint:
	flake8 bitshares*

.PHONY: test
test:
	python3 setup.py test

.PHONY: tox
tox:
	tox

.PHONY: build
build:
	python3 setup.py build

.PHONY: install
install: build
	python3 setup.py install

.PHONY: install-user
install-user: build
	python3 setup.py install --user

.PHONY: git
git:
	git push --all
	git push --tags

.PHONY: check
check:
	python3 setup.py check

.PHONY: docs
docs:
	sphinx-apidoc -d 6 -e -f -o docs . *.py tests
	make -C docs clean html
