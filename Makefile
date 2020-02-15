.PHONY: help build test clean dist install coverage pre-release release \
        docs clean-docs lint tags coverage-view changelog \
        clean-pyc clean-build clean-patch clean-local clean-test-data \
        test-all test-data build-release freeze-release tag-release \
        pypi-release web-release github-release cookiecutter requirements
SRC_DIRS = ./eyed3
TEST_DIR = ./test
NAME ?= Travis Shirk
EMAIL ?= travis@pobox.com
GITHUB_USER ?= nicfit
GITHUB_REPO ?= eyeD3
PYPI_REPO = pypitest
PROJECT_NAME = $(shell python setup.py --name 2> /dev/null)
VERSION = $(shell python setup.py --version 2> /dev/null)
RELEASE_NAME = $(shell python setup.py --release-name 2> /dev/null)
RELEASE_TAG = v$(VERSION)
CHANGELOG = HISTORY.rst
CHANGELOG_HEADER = v${VERSION} ($(shell date --iso-8601))$(if ${RELEASE_NAME}, : ${RELEASE_NAME},)
TEST_DATA = eyeD3-test-data
TEST_DATA_FILE = ${TEST_DATA}.tgz
TEST_DATA_DIR ?= $(shell pwd)/test

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
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on various versions of Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "release - package and upload a release"
	@echo "          PYPI_REPO=[pypitest]|pypi"
	@echo "pre-release - check repo and show version, generate changelog, etc."
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"
	@echo "build - build package source files"
	@echo ""
	@echo "Options:"
	@echo "TEST_PDB - If defined PDB options are added when 'pytest' is invoked"
	@echo "BROWSER - HTML viewer used by docs-view/coverage-view"
	@echo "CC_MERGE - Set to no to disable cookiecutter merging."
	@echo "CC_OPTS - OVerrided the default options (--no-input) with your own."

build:
	python setup.py build

clean: clean-local clean-build clean-pyc clean-test clean-patch clean-docs

clean-local:
	-rm tags
	-rm all.id3 example.id3

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -rf eyeD3.egg-info
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	find . -name '.pytest_cache' -type d -exec rm -rf {} +
	-rm .testmondata
	-rm examples/*.id3

clean-patch:
	find . -name '*.rej' -exec rm -f '{}' \;
	find . -name '*.orig' -exec rm -f '{}' \;

lint:
	tox -e lint

_PYTEST_OPTS=
ifdef TEST_PDB
    _PDB_OPTS=--pdb -s
endif
test:
	tox -e default -- $(_PYTEST_OPTS) $(_PDB_OPTS)

test-devel:
	-tox -e default -- --testmon

test-all:
	tox -e clean
	tox --parallel=all
	tox -e coverage

test-data:
	# Move these to eyed3.nicfit.net
	test -f ${TEST_DATA_DIR}/${TEST_DATA_FILE} || \
		wget --quiet "http://eyed3.nicfit.net/releases/${TEST_DATA_FILE}" \
		     -O ${TEST_DATA_DIR}/${TEST_DATA_FILE}
	tar xzf ${TEST_DATA_DIR}/${TEST_DATA_FILE} -C ${TEST_DATA_DIR}
	cd test && rm -f ./data && ln -s ${TEST_DATA_DIR}/${TEST_DATA} ./data

clean-test-data:
	-rm test/data
	-rm test/${TEST_DATA_FILE}

pkg-test-data:
	test -d build || mkdir build
	tar czf ./build/${TEST_DATA_FILE} -h --exclude-vcs -C ./test \
		    ./eyeD3-test-data

publish-test-data:
	scp ./build/${TEST_DATA_FILE} eyed3.nicfit.net:./data1/eyeD3-releases/

coverage:
	tox -e coverage

coverage-view:
	@if [ ! -f build/tests/coverage/index.html ]; then \
		${MAKE} coverage; \
	fi
	@${BROWSER} build/tests/coverage/index.html

docs:
	rm -f docs/eyed3.rst
	rm -f docs/modules.rst
	sphinx-apidoc --force -H $(PROJECT_NAME) -V $(VERSION) -o docs/ ${SRC_DIRS}
	$(MAKE) -C docs clean
	etc/mycog.py
	$(MAKE) -C docs html
	-rm example.id3

docs-dist: docs
	test -d dist || mkdir dist
	cd docs/_build && \
	    tar czvf ../../dist/${PROJECT_NAME}-${VERSION}_docs.tar.gz html

docs-view: docs
	$(BROWSER) docs/_build/html/index.html

clean-docs:
	$(MAKE) -C docs clean
	-rm README.html

pre-release: lint test changelog requirements
	@# Keep docs off pre-release target list, else it is pruned during 'release' but
	@# after a clean.
	@$(MAKE) docs
	@echo "VERSION: $(VERSION)"
	@echo "RELEASE_TAG: $(RELEASE_TAG)"
	@echo "RELEASE_NAME: $(RELEASE_NAME)"
	tox -e check-manifest
	@if git tag -l | grep -E '^$(shell echo $${RELEASE_TAG} | sed 's|\.|.|g')$$' > /dev/null; then \
        echo "Version tag '${RELEASE_TAG}' already exists!"; \
        false; \
    fi
	IFS=$$'\n';\
	for auth in `git authors --list | sed 's/.* <\(.*\)>/\1/' | grep -v users.noreply.github.com`; do \
		echo "Checking $$auth...";\
		grep "$$auth" AUTHORS.rst || echo "  * $$auth" >> AUTHORS.rst;\
	done
	@test -n "${GITHUB_USER}" || (echo "GITHUB_USER not set, needed for github" && false)
	@test -n "${GITHUB_TOKEN}" || (echo "GITHUB_TOKEN not set, needed for github" && false)
	@github-release --version    # Just a exe existence check
	@git status -s -b

requirements:
	tox -e requirements

changelog:
	last=`git tag -l --sort=version:refname | grep '^v[0-9]' | tail -n1`;\
	if ! grep "${CHANGELOG_HEADER}" ${CHANGELOG} > /dev/null; then \
		rm -f ${CHANGELOG}.new; \
		if test -n "$$last"; then \
			gitchangelog --author-format=email \
			             --omit-author="travis@pobox.com" $${last}..HEAD |\
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
	@(git diff --quiet && git diff --quiet --staged) || \
        (printf "\n!!! Working repo has uncommited/unstaged changes. !!!\n" && \
         printf "\nCommit and try again.\n" && false)

tag-release:
	git tag -a $(RELEASE_TAG) -m "Release $(RELEASE_TAG)"
	git push --tags origin

release: pre-release freeze-release build-release tag-release upload-release

github-release:
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
        echo "Uploading: $$file"; \
        github-release upload --user "${GITHUB_USER}" --repo ${GITHUB_REPO} \
                   --tag ${RELEASE_TAG} --name $${file} --file dist/$${file}; \
    done

web-release:
	for f in `find dist -type f`; do \
	    scp $$f eyed3.nicfit.net:./data1/eyeD3-releases/`basename $$f`; \
	done

upload-release: pypi-release github-release web-release

pypi-release:
	for f in `find dist -type f -name ${PROJECT_NAME}-${VERSION}.tar.gz \
              -o -name \*.egg -o -name \*.whl`; do \
        if test -f $$f ; then \
            twine upload --verbose -r ${PYPI_REPO} --skip-existing $$f ; \
        fi \
	done

sdist: build
	python setup.py sdist --formats=gztar,zip
	python setup.py bdist_egg
	python setup.py bdist_wheel

dist: clean sdist docs-dist
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

CC_MERGE ?= yes
CC_OPTS ?= --no-input
GIT_COMMIT_HOOK = .git/hooks/commit-msg
cookiecutter:
	tmp_d=`mktemp -d`; cc_d=$$tmp_d/eyeD3; \
	if test "${CC_MERGE}" == "no"; then \
		nicfit cookiecutter ${CC_OPTS} "$${tmp_d}"; \
		git -C "$$cc_d" diff; \
		git -C "$$cc_d" status -s -b; \
	else \
		nicfit cookiecutter --merge ${CC_OPTS} "$${tmp_d}" \
		       --extra-merge ${GIT_COMMIT_HOOK} ${GIT_COMMIT_HOOK};\
	fi; \
	rm -rf $$tmp_d


