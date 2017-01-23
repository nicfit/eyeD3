.PHONY: clean-pyc clean-build clean-patch clean-local docs clean help lint \
        test test-all coverage docs release dist tags build install \
        build-release pre-release freeze-release _tag-release _upload-release \
        _pypi-release _github-release clean-docs cookiecutter changelog \
        _web-release
SRC_DIRS = ./src/eyed3
TEST_DIR = ./src/test
TEMP_DIR ?= ./tmp
CC_DIR = ${TEMP_DIR}/eyeD3
NAME ?= Travis Shirk
EMAIL ?= travis@pobox.com
GITHUB_USER ?= nicfit
GITHUB_REPO ?= eyeD3
PYPI_REPO = pypitest
VERSION = $(shell python setup.py --version 2> /dev/null)
RELEASE_NAME = $(shell python setup.py --release-name 2> /dev/null)
CHANGELOG = HISTORY.rst
CHANGELOG_HEADER = v${VERSION} ($(shell date --iso-8601))$(if ${RELEASE_NAME}, : ${RELEASE_NAME},)

help:
	@echo "test - run tests quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "clean-docs - remove autogenerating doc artifacts"
	@echo "clean-patch - remove patch artifacts (.rej, .orig)"
	@echo "build - byte-compile python files and generate other build objects"
	@echo "lint - check style with flake8"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "test-all - run tests on various Python versions with tox"
	@echo "release - package and upload a release"
	@echo "          PYPI_REPO=[pypitest]|pypi"
	@echo "pre-release - check repo and show version"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"
	@echo ""
	@echo "Options:"
	@echo "TEST_PDB - If defined PDB options are added when 'pytest' is invoked"
	@echo "BROWSER - HTML viewer used by docs-view/coverage-view"

build:
	python setup.py build

clean: clean-local clean-build clean-pyc clean-test clean-patch clean-docs
	rm -rf tags

clean-local:
	@# XXX Add new clean targets here.

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -rf ${TEMP_DIR}

clean-patch:
	find . -name '*.rej' -exec rm -f '{}' \;
	find . -name '*.orig' -exec rm -f '{}' \;

lint:
	flake8 $(SRC_DIRS)

_PYTEST_OPTS=

ifdef TEST_PDB
    _PDB_OPTS=--pdb -s
endif

test:
	pytest $(_PYTEST_OPTS) $(_PDB_OPTS) ${TEST_DIR}

test-all:
	tox


coverage:
	pytest --cov=./src/eyed3 \
           --cov-report=html --cov-report term \
           --cov-config=setup.cfg ${TEST_DIR}

coverage-view: coverage
	${BROWSER} build/tests/coverage/index.html;\

docs:
	rm -f docs/eyed3.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ ${SRC_DIRS}
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

docs-view: docs
	$(BROWSER) docs/_build/html/index.html;\

clean-docs:
	# TODO
	#$(MAKE) -C docs clean
	-rm README.html

# FIXME: never been tested
servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

pre-release: lint test changelog
	@test -n "${GITHUB_USER}" || (echo "GITHUB_USER not set, needed for github" && false)
	@test -n "${GITHUB_TOKEN}" || (echo "GITHUB_TOKEN not set, needed for github" && false)
	@echo "VERSION: $(VERSION)"
	$(eval RELEASE_TAG = v${VERSION})
	@echo "RELEASE_TAG: $(RELEASE_TAG)"
	@echo "RELEASE_NAME: $(RELEASE_NAME)"
	check-manifest
	@if git tag -l | grep ${RELEASE_TAG} > /dev/null; then \
        echo "Version tag '${RELEASE_TAG}' already exists!"; \
        false; \
    fi
	IFS=$$'\n';\
	for auth in `git authors --list`; do \
		echo "Checking $$auth...";\
		grep "$$auth" AUTHORS.rst || echo "* $$auth" >> AUTHORS.rst;\
	done
	@github-release --version    # Just a exe existence check

changelog:
	last=`git tag -l --sort=version:refname | grep '^v[0-9]' | tail -n1`;\
	if ! grep "${CHANGELOG_HEADER}" ${CHANGELOG} > /dev/null; then \
		rm -f ${CHANGELOG}.new; \
		if test -n "$$last"; then \
			gitchangelog show ^$${last} |\
			  sed "s|^%%version%% .*|${CHANGELOG_HEADER}|" |\
			  sed '/^.. :changelog:/ r/dev/stdin' ${CHANGELOG} \
			 > ${CHANGELOG}.new; \
		else \
			cat ${CHANGELOG} |\
			  sed "s/^%%version%% .*/${CHANGELOG_HEADER}/" \
			> ${CHANGELOG}.new;\
		fi; \
		mv ${CHANGELOG}.new ${CHANGELOG}; \
	fi

build-release: test-all dist

freeze-release:
	@# TODO: check for incoming
	@(git diff --quiet && git diff --quiet --staged) || \
        (printf "\n!!! Working repo has uncommited/unstaged changes. !!!\n" && \
         printf "\nCommit and try again.\n" && false)

_tag-release:
	git tag -a $(RELEASE_TAG) -m "Release $(RELEASE_TAG)"
	git push --tags origin

release: pre-release freeze-release build-release _tag-release _upload-release


_github-release:
	name="${RELEASE_TAG}"; \
    if test -n "${RELEASE_NAME}"; then \
        name="${RELEASE_TAG} (${RELEASE_NAME})"; \
    fi; \
    prerelease=""; \
    if echo "${RELEASE_TAG}" | grep '[^v0-9\.]'; then \
        prerelease="--pre-release"; \
    fi; \
    echo "NAME: $$name"; \
    echo "PRERELEASE: $$prerelease"; \
    github-release --verbose release --user "${GITHUB_USER}" \
                   --repo ${GITHUB_REPO} --tag ${RELEASE_TAG} \
                   --name "$${name}" $${prerelease}
	for file in $$(find dist -type f -exec basename {} \;) ; do \
        echo "FILE: $$file"; \
        github-release upload --user "${GITHUB_USER}" --repo ${GITHUB_REPO} \
                   --tag ${RELEASE_TAG} --name $${file} --file dist/$${file}; \
    done


_web-release:
	# TODO
	#find dist -type f -exec scp register -r ${PYPI_REPO} {} \;
	# Not implemented
	true


_upload-release: _github-release _pypi-release _web-release


_pypi-release:
	find dist -type f -exec twine register -r ${PYPI_REPO} {} \;
	find dist -type f -exec twine upload -r ${PYPI_REPO} --skip-existing {} \;

dist: clean
	python setup.py sdist
	python setup.py bdist_egg
	python setup.py bdist_wheel
	@# The cd dist keeps the dist/ prefix out of the md5sum files
	cd dist && \
    for f in $$(ls); do \
        md5sum $${f} > $${f}.md5; \
    done
	ls -l dist

install: clean
	python setup.py install

tags:
	ctags -R ${SRC_DIRS}

README.html: README.rst
	rst2html5.py README.rst >| README.html
	if test -n "${BROWSER}"; then \
		${BROWSER} README.html;\
	fi

CC_DIFF ?= gvimdiff -geometry 169x60 -f
cookiecutter:
	rm -rf ${TEMP_DIR}
	git clone --branch `git rev-parse --abbrev-ref HEAD` . ${CC_DIR}
	nicfit cookiecutter --config-file ./.cookiecutter.json --no-input ${TEMP_DIR}
	if test "${CC_DIFF}" == "no"; then \
		git -C ${CC_DIR} diff; \
		git -C ${CC_DIR} status -s -b; \
	else \
		for f in `git -C ${CC_DIR} status --porcelain | \
		                 awk '{print $$2}'`; do \
			if test -f ${CC_DIR}/$$f; then \
				diff ${CC_DIR}/$$f ./$$f > /dev/null || \
				  ${CC_DIFF} ${CC_DIR}/$$f ./$$f; \
			fi \
		done; \
		diff ${CC_DIR}/.git/hooks/commit-msg .git/hooks/commit-msg >/dev/null || \
		  ${CC_DIFF} ${CC_DIR}/.git/hooks/commit-msg ./.git/hooks/commit-msg; \
	fi
