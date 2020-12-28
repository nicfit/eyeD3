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

## Defaults

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


all: build test  ## Build and test


## Config
PROJECT_NAME = $(shell python setup.py --name 2> /dev/null)
VERSION = $(shell python setup.py --version 2> /dev/null)
SRC_DIRS = ./eyed3
ABOUT_PY = eyed3/__regarding__.py
GITHUB_USER = nicfit
GITHUB_REPO = eyeD3
RELEASE_NAME = $(shell sed -n "s/^release_name = \"\(.*\)\"/\1/p" pyproject.toml)
RELEASE_TAG = v$(VERSION)
CHANGELOG = HISTORY.rst
CHANGELOG_HEADER = v${VERSION} ($(shell date --iso-8601))$(if ${RELEASE_NAME}, : ${RELEASE_NAME},)
TEST_DATA = eyeD3-test-data
TEST_DATA_FILE = ${TEST_DATA}.tgz


## Build
.PHONY: build
build: $(ABOUT_PY) setup.py  ## Build the project

setup.py: pyproject.toml poetry.lock
	dephell deps convert --from pyproject.toml --to setup.py

$(ABOUT_PY): pyproject.toml
	regarding -o $@

# Note, this clean rule is NOT to be called as part of `clean`
clean-autogen:
	-rm $(ABOUT_PY) setup.py


## Clean
clean: clean-test clean-dist clean-local clean-docs  # Clean the project
	rm -rf ./build
	rm -rf eye{d,D}3.egg-info
	rm -fr .eggs/
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-local:
	-rm tags
	-rm all.id3 example.id3
	find . -name '*.rej' -exec rm -f '{}' \;
	find . -name '*.orig' -exec rm -f '{}' \;
	find . -type f -name '*~' | xargs -r rm


## Test
.PHONY: test
test:  ## Run tests with default python
	pytest $(PYTEST_ARGS)

test-all:  ## Run tests with all supported versions of Python
	tox --parallel=all $(PYTEST_ARGS)

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


## Documentation
.PHONY: docs
docs:  ## Generate project documentation with Sphinx
	rm -f docs/eyed3.rst
	rm -f docs/modules.rst
	sphinx-apidoc --force -H "$(shell echo $(PROJECT_NAME) | tr '[:upper:]' '[:lower:]') module" -V $(VERSION) -o docs/ ${SRC_DIRS}
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


lint:  ## Check coding style
	flake8 $(SRC_DIRS)


## Distribute
.PHONY: dist
dist: clean sdist bdist docs-dist  ## Create source and binary distribution files
	@# The cd dist keeps the dist/ prefix out of the md5sum files
	@cd dist && \
	for f in $$(ls); do \
		md5sum $${f} > $${f}.md5; \
	done
	@ls dist

sdist: build
	poetry build --format sdist

bdist: build
	poetry build --format wheel

clean-dist:  ## Clean distribution artifacts (included in `clean`)
	rm -rf dist

check-manifest:
	check-manifest

_check-version-tag:
	@if git tag -l | grep -E '^$(shell echo ${RELEASE_TAG} | sed 's|\.|.|g')$$' > /dev/null; then \
        echo "Version tag '${RELEASE_TAG}' already exists!"; \
        false; \
    fi

authors:
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
	poetry install --no-dev

install-dev:  ## Install project, dependencies, and developer tools
	poetry install -E test


## Release
release: pre-release clean install-dev \
         _freeze-release dist _tag-release \
          upload-release

pre-release: clean-autogen build _check-version-tag \
	         check-manifest authors changelog test-all
	@# Keep docs off pre-release target list, else it is pruned during 'release' but
	@# after a clean.
	@$(MAKE) docs
	@test -n "${GITHUB_USER}" || (echo "GITHUB_USER not set, needed for github" && false)
	@test -n "${GITHUB_TOKEN}" || (echo "GITHUB_TOKEN not set, needed for github" && false)
	@github-release --version    # Just a exe existence check
	@git status -s -b

bump-release: requirements
	@# TODO: is not a pre-release, clear release_name
	poetry version $(BUMP)

.PHONY: requirements
requirements:
	poetry show --outdated
	poetry update --lock
	poetry export -f requirements.txt --without-hashes\
		--output requirements/requirements.txt
	poetry export -f requirements.txt --without-hashes\
 		--output requirements/test-requirements.txt -E test
	poetry export -f requirements.txt --without-hashes\
 		--output requirements/dev-requirements.txt -E dev
	poetry export -f requirements.txt --without-hashes\
 		--output requirements/extra-requirements.txt \
		-E display-plugin -E art-plugin -E yaml-plugin
	$(MAKE) build

upload-release: _pypi-release _github-release _web-release

_pypi-release:
	poetry publish -r ${PYPI_REPO}

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
        echo "Uploading: $$file"; \
        github-release upload --user "${GITHUB_USER}" --repo ${GITHUB_REPO} \
                   --tag ${RELEASE_TAG} --name $${file} --file dist/$${file}; \
    done

_web-release:
	for f in `find dist -type f`; do \
	    scp $$f eyed3.nicfit.net:./data1/eyeD3-releases/`basename $$f`; \
	done

_freeze-release:
	@(git diff --quiet && git diff --quiet --staged) || \
        (printf "\n!!! Working repo has uncommitted/un-staged changes. !!!\n" && \
         printf "\nCommit and try again.\n" && false)

_tag-release:
	git tag -a $(RELEASE_TAG) -m "Release $(RELEASE_TAG)"
	git push --tags origin

changelog:
	@last=`git tag -l --sort=version:refname | grep '^v[0-9]' | tail -n1`;\
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


## MISC
README.html: README.rst
	rst2html5.py README.rst >| README.html
	if test -n "${BROWSER}"; then \
		${BROWSER} README.html;\
	fi

GIT_COMMIT_HOOK = .git/hooks/commit-msg
cookiecutter:
	tmp_d=`mktemp -d`; cc_d=$$tmp_d/eyeD3; \
	if test "${CC_MERGE}" = "no"; then \
		nicfit cookiecutter ${CC_OPTS} "$${tmp_d}"; \
		git -C "$$cc_d" diff; \
		git -C "$$cc_d" status -s -b; \
	else \
		nicfit cookiecutter --merge ${CC_OPTS} "$${tmp_d}" \
		       --extra-merge ${GIT_COMMIT_HOOK} ${GIT_COMMIT_HOOK};\
	fi; \
	rm -rf $$tmp_d

## Runtime environment
venv:
	source /usr/bin/virtualenvwrapper.sh && \
 		mkvirtualenv eyeD3 && \
 		pip install -U pip && \
		poetry install --no-dev

clean-venv:
	source /usr/bin/virtualenvwrapper.sh && \
 		rmvirtualenv eyeD3
