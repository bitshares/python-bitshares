.PHONY: clean-pyc clean-build docs

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr __pycache__/ .eggs/ .cache/ .tox/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 bitsharesapi bitsharesbase examples

test:
	python3 setup.py test

build:
	python3 setup.py build

install: build
	python3 setup.py install

install-user: build
	python3 setup.py install --user

git:
	git push --all
	git push --tags

check:
	python3 setup.py check

dist:
	python3 setup.py sdist bdist_wheel
	python3 setup.py bdist_wheel
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
	#twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	#python3 setup.py sdist upload -r pypi
	#python3 setup.py bdist_wheel upload

docs:
	SPHINX_APIDOC_OPTIONS="members,undoc-members,show-inheritance,inherited-members" sphinx-apidoc -d 6 -e -f -o docs . *.py tests
	make -C docs clean html

prepare: clean test docs authors

release: clean check dist git

authors:
	git shortlog -e -s -n > AUTHORS
