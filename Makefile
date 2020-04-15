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

upload:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

docs:
	SPHINX_APIDOC_OPTIONS="members,undoc-members,show-inheritance,inherited-members" sphinx-apidoc -d 6 -e -f -o docs . *.py tests
	make -C docs clean html

docs_store:
	git add docs
	-git commit -m "Updating docs/"

authors:
	git shortlog -e -s -n > AUTHORS

authors_store:
	git add AUTHORS
	-git commit -m "Updating Authors"

semver: semver-release semver-updates

semver-release:
	-semversioner release

semver-updates:
	semversioner changelog > CHANGELOG.md
	$(eval CURRENT_VERSION = $(shell semversioner current-version))
	sed -i "s/^__version__.*/__version__ = \"$(CURRENT_VERSION)\"/" setup.py
	-git add .changes setup.py CHANGELOG.md
	-git commit -m "semversioner release updates" --no-verify
	-git flow release start $(CURRENT_VERSION)
	git flow release finish $(CURRENT_VERSION)

prerelease: test docs docs_store authors authors_store
release: prerelease semver clean build check dist upload git
