SHELL := /bin/bash
.DEFAULT_GOAL := build

## User settings
PYTEST_ARGS ?= ./tests
PYPI_REPO ?= pypi
BUMP ?= prerelease
TEST_DATA_DIR ?= $(shell pwd)/tests
CC_MERGE ?= yes
CC_OPTS ?= --no-input

ifdef TERM
BOLD_COLOR = $(shell tput bold)
HELP_COLOR = $(shell tput setaf 6)
HEADER_COLOR = $(BOLD_COLOR)$(shell tput setaf 2)
NO_COLOR = $(shell tput sgr0)
endif

help:  ## List all commands
	@printf "\n$(BOLD_COLOR)***** eyeD3 Makefile help *****$(NO_COLOR)\n"
	@# This code borrowed from https://github.com/jedie/poetry-publish/blob/master/Makefile
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@printf "$(BOLD_COLOR)Options:$(NO_COLOR)\n"
	@printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n" PYTEST_ARGS "If defined PDB options are added when 'pytest' is invoked"
	@printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n" PYPI_REPO "The package index to publish, 'pypi' by default."
	@printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n" BROWSER "HTML viewer used by docs-view/coverage-view"
	@printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n" CC_MERGE "Set to no to disable cookiecutter merging."
	@printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n" CC_OPTS "OVerrided the default options (--no-input) with your own."
	@echo ""


all: clean build test  ## Build and test


## Config
PROJECT_NAME := $(shell sed -n "s/^name = \"\(.*\)\"/\1/p" pyproject.toml)
ifeq ($(strip $(PROJECT_NAME)),)
  $(error "PROJECT_NAME not set")
endif
VERSION := $(shell sed -n "s/^version = \"\(.*\)\"/\1/p" pyproject.toml)
ifeq ($(strip $(VERSION)),)
  $(error "VERSION not set")
endif
RELEASE_NAME = $(shell sed -n "s/^release_name = \"\(.*\)\"/\1/p" pyproject.toml)
RELEASE_TAG := v$(VERSION)

SRC_DIRS = ./eyed3
GITHUB_USER = nicfit
GITHUB_REPO = eyeD3
CHANGELOG = HISTORY.rst
CHANGELOG_HEADER = v${VERSION} ($(shell date --iso-8601))$(if ${RELEASE_NAME}, : ${RELEASE_NAME},)
TEST_DATA = eyeD3-test-data
TEST_DATA_FILE = ${TEST_DATA}.tgz
ABOUT_PY := eyed3/__regarding__.py


## Build
.PHONY: build
BUILD_OPTS ?=
build: $(ABOUT_PY)  ## Build the project
	pdm build -d dist/ $(BUILD_OPTS)

$(ABOUT_PY): pyproject.toml
	regarding -o $@


## Clean
clean: clean-test clean-dist clean-local clean-docs  # Clean the project
	touch pyproject.toml
	rm -rf ./build
	rm -rf eye{d,D}3.egg-info
	rm -fr .eggs/
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -type d -exec rm -fr {} +

clean-local:
	-rm tags
	-rm all.id3 example.id3
	find . -name '*.rej' -exec rm -f '{}' \;
	find . -name '*.orig' -exec rm -f '{}' \;
	find . -type f -name '*~' | xargs -r rm


### Test
.PHONY: test
test:  ## Run tests with default python
	tox -e py,lint

SKIP_TEST_ALL ?= no
test-all:  ## Run tests with all supported versions of Python
	@if [ "$(SKIP_TEST_ALL)" != yes ]; then \
	    tox --parallel=all ;\
	fi

test-data:
	# Move these to eyed3.nicfit.net
	test -f ${TEST_DATA_DIR}/${TEST_DATA_FILE} || \
		wget --quiet "http://eyed3.nicfit.net/releases/${TEST_DATA_FILE}" \
		     -O ${TEST_DATA_DIR}/${TEST_DATA_FILE}
	tar xzf ${TEST_DATA_DIR}/${TEST_DATA_FILE} -C ${TEST_DATA_DIR}
	cd tests && rm -f ./data && ln -s ${TEST_DATA_DIR}/${TEST_DATA} ./data

clean-test:
	rm -fr .tox/
	rm -f .coverage
	find . -name '.pytest_cache' -type d -exec rm -rf {} +
	-rm .testmondata
	-rm examples/*.id3

clean-test-data:
	-rm tests/data
	-rm tests/${TEST_DATA_FILE}

pkg-test-data:
	test -d build || mkdir build
	tar czf ./build/${TEST_DATA_FILE} -h --exclude-vcs -C ./tests \
		    ./eyeD3-test-data

publish-test-data: pkg-test-data
	scp ./build/${TEST_DATA_FILE} eyed3.nicfit.net:./data1/eyeD3-releases/

coverage:
	coverage run --source $(SRC_DIRS) -m pytest $(PYTEST_ARGS)
	coverage report
	coverage html

coverage-view:
	@if [ ! -f build/tests/coverage/index.html ]; then \
		${MAKE} coverage; \
	fi
	@${BROWSER} build/tests/coverage/index.html

lint:  ## Check coding style
	tox -e lint


### Documentation
.PHONY: docs
docs:  ## Generate project documentation with Sphinx
	rm -f docs/eyed3.rst
	rm -f docs/modules.rst
	sphinx-apidoc --force -H "$(shell echo $(PROJECT_NAME) | tr '[:upper:]' '[:lower:]') module" -V $(VERSION) -o docs/ ${SRC_DIRS}
	$(MAKE) -C docs clean
	etc/mycog.py
	$(MAKE) -C docs html
	-rm example.id3

DOCS_DIST := $(PROJECT_NAME)-$(VERSION)-docs.tar.gz
docs-dist: docs
	cd docs/_build && tar czvf ./$(DOCS_DIST) html

docs-view: docs
	$(BROWSER) docs/_build/html/index.html

clean-docs:
	if which sphinx-build >/dev/null 2>&1; then \
	    $(MAKE) -C docs clean;\
	fi
	-rm README.html


### Distribute
.PHONY: dist
dist: clean-dist lint all docs-dist ## Create source and binary distribution files

_dist-md5:
	@# The cd dist/docs keeps the dist/ prefix out of the md5sum files
	cd docs/_build/ &&  md5sum $(DOCS_DIST) >| $(DOCS_DIST).md5
	@cd dist && \
	for f in $$(ls -I '*.md5'); do \
		md5sum $${f} >| $${f}.md5; \
	done
	@ls -l docs/_build/$(DOCS_DIST)* dist


clean-dist:  ## Clean distribution artifacts (included in `clean`)
	rm -rf dist

check-manifest:
	check-manifest

release-tag: _check-clean-repo _check-version-tag _check-main-branch
	@if ! git tag --annotate $(RELEASE_TAG) -m "$(RELEASE_NAME)" 2> /dev/null; then \
       echo "!!! $(RELEASE_TAG) already exists; update pyproject.toml !!!"; \
       exit 1; \
    fi
	git push origin $(RELEASE_TAG)

authors:
	@# requires git-extras
	@git authors --list | while read auth ; do \
  		email=`echo "$$auth" | awk 'match($$0, /.*<(.*)>/, m)  {print m[1]}'`;\
		echo "Checking $$email...";\
  		if echo "$$email" | grep -v 'users.noreply.github.com'\
  		                  | grep -v 'github-bot@pyup.io' \
  		                  > /dev/null ; then \
			grep "$$email" AUTHORS.rst > /dev/null || echo "  * $$auth" >> AUTHORS.rst;\
		fi;\
	done


## Install
install:  ## Install project and dependencies
	python -m pip install --editable .

install-dev:  ## Install project, dependencies, and developer tools
	python -m pip install --editable .[dev,test]

install-extra:  ## Install project, dependencies, and developer tools
	python -m pip install --editable .[art-plugin,yaml-plugin]

install-all: install install-extra install-dev


## Release
.PHONY: release
release: _check-on-release-tag _check-clean-repo _check-gh _check-pypi dist publish-release

pre-release: _check-version-tag dist check-manifest test-all requirements authors _check-clean-repo
#pre-release: #	         changelog

# Order is import here
publish-release: _pypi-publish _web-publish _github-publish _docs-publish

_pypi-publish:
	pdm publish --no-build -r $(PYPI_REPO) --skip-existing  --dest ./dist

_web-publish: _dist-md5
	for f in `find ./dist -type f`; do \
	    scp $$f eyed3.nicfit.net:./data1/eyeD3-releases/`basename $$f`; \
	done

_docs-publish:
	# TODO: READTHEDOCS move latest to release version

_github-publish:
	@# TODO: --prerelease if appropriate
	@# TODO: --notes-file when release notes are available
	@# TODO: --latest=false when prerelease is used
	gh release --repo nicfit/eyeD3 create $(RELEASE_TAG) --verify-tag \
               --title "$(RELEASE_TAG) ($(RELEASE_NAME))" \
               --draft \
               --generate-notes ./dist/*.tar.gz ./dist/*.whl


### MISC
#
#GIT_COMMIT_HOOK = .git/hooks/commit-msg
#cookiecutter:
#	tmp_d=`mktemp -d`; cc_d=$$tmp_d/eyeD3; \
#	if test "${CC_MERGE}" = "no"; then \
#		nicfit cookiecutter ${CC_OPTS} "$${tmp_d}"; \
#		git -C "$$cc_d" diff; \
#		git -C "$$cc_d" status -s -b; \
#	else \
#		nicfit cookiecutter --merge ${CC_OPTS} "$${tmp_d}" \
#		       --extra-merge ${GIT_COMMIT_HOOK} ${GIT_COMMIT_HOOK};\
#	fi; \
#	rm -rf $$tmp_d

## Runtime environment
VENV_NAME ?= dev-eyeD3
VENV_DIR ?= $(HOME)/.virtualenvs
VENV_ACTIVATE := $(VENV_DIR)/$(VENV_NAME)/bin/activate
clean-venv:
	test -n "$(VENV_DIR)" && test -n "$(VENV_NAME)" && rm -rf $(VENV_DIR)/$(VENV_NAME)

venv:
	python -m venv --upgrade-deps $(VENV_DIR)/$(VENV_NAME)
	@printf "\n$(BOLD_COLOR)To activate the virtualenv:$(NO_COLOR) source $(VENV_ACTIVATE)\n"
	@printf "$(BOLD_COLOR)To deactivate the virtualenv:$(NO_COLOR) deactivate\n\n"


_check-version-tag:
	@if git tag -l | grep -E '^$(shell echo ${RELEASE_TAG} | sed 's|\.|.|g')$$' > /dev/null; then \
        echo "!!! Version tag '${RELEASE_TAG}' already exists !!!"; \
        false; \
    else\
        echo "Version tag '${RELEASE_TAG}' is available."; \
    fi

MAIN_BRANCH ?= 0.9.x
_check-main-branch:
	@if [ `git branch --show-current` != $(MAIN_BRANCH) ]; then \
	   echo "!!! Not on $(MAIN_BRANCH) branch. !!!"; \
	   exit 1; \
	fi

_check-on-release-tag:
	@if [ "`git describe --tags`" != "$(RELEASE_TAG)" ]; then \
	   echo "!!! Not on $(RELEASE_TAG) checkout. !!!"; \
	   exit 1; \
	fi

_check-clean-repo:
	@if [ -n "`git status --porcelain --untracked-files=no`" ]; then \
	   echo "!!! Working repo has uncommitted/un-staged changes. !!!"; \
	   exit 1; \
	else \
	   echo "Repo clean.";\
	fi

_check-gh:
	@test -n "${GH_TOKEN}" || (echo "GH_TOKEN not set, needed for gh" && false)
	@gh --help > /dev/null || (echo "gh not installed" && false)

_check-pypi:
	@(test -n "${PDM_PUBLISH_USERNAME}" && test -n "${PDM_PUBLISH_PASSWORD}") || \
	 	(echo "PDM_BUBLISH_* not set, needed for PyPI publish" && false)

#bump-release:
#	@# TODO: is not a pre-release, clear release_name
#	poetry version $(BUMP)

.PHONY: requirements
requirements:
	pdm lock -G:all
	pdm export --prod --no-hashes >| requirements/requirements.txt
	pdm export -G test,dev --no-hashes  >| requirements/dev-requirements.txt
	pdm export -G yaml-plugim,art-plugin --no-hashes  >| requirements/plugin-requirements.txt
