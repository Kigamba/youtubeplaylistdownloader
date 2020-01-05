include init.mk

SHELL := bash

# Python package to use with conda install
CONDA_CPYTHON_PACKAGE := python=$(CPYTHON_VERSION)
CONDA_PYPY_PACKAGE := pypy$(PYPY_VERSION)

PACKAGE_NAME := youtube_playlist_downloader

CONDA_ENV := ./.conda_env_$(PYTHON_IMP)
CONDA_CHANNELS_OPT := -c defaults -c conda-forge
# This eval is needed because conda functions are not exported to subshells
# Not calling source ~/. .bashrc here since it exits early for
# non interactive shell (which is what being used here. See 'SHELL')
CONDA_INIT_CMD := eval "$$(command conda 'shell.bash' 'hook' 2> /dev/null)"

CONDA_ACTIVATE = $(CONDA_INIT_CMD) && conda activate $(CONDA_ENV)
CONDA_DEACTIVATE = conda deactivate

PYPY_EXPORT_PYTHONPATH_CMD := export PYTHONPATH=$$(conda info -q --json | jq -r .active_prefix)/lib/python$(CPYTHON_VERSION)/site-packages

ifeq ($(PYTHON_IMP),cpython)
	PYTHON_CMD := $(CPYTHON_BIN)
	CONDA_POST_ACTIVATE := :
else
	PYTHON_CMD := $(PYPY_BIN)
	# Pypy needs to have access to cpython packages installed
	CONDA_POST_ACTIVATE := $(PYPY_EXPORT_PYTHONPATH_CMD)

	# Install both python with pypy since it's installed anyways along with other requirement packages
	# Pytest is failing with pypy 3.5 without pathlib2
	CONDA_ADDITIONAL_PACKAGES := pathlib2 $(CONDA_PYPY_PACKAGE)
endif

############################## Conda Targets ###################################

# This eval is needed because conda functions are not exported to subshells
# Not calling source ~/. .bashrc here since it exits early for
# non interactive shell (which is what being used here. See 'SHELL')
.PHONY: setup
setup: create-conda-env conda-install-packages

.PHONY: create-conda-env
create-conda-env:
	$(CONDA_INIT_CMD) && \
		{ conda list -p $(CONDA_ENV) -q -f python > /dev/null 2>&1 && \
		echo "Conda environment '$(CONDA_ENV)' exiss." ; } || \
		{ echo "Creating conda environment: '$(CONDA_ENV)'..." && \
		conda create -yq -p $(CONDA_ENV) $(CONDA_CPYTHON_PACKAGE) $(CONDA_CHANNELS_OPT); }

.PHONY: conda-install-packages
conda-install-packages:
	$(CONDA_ACTIVATE) && \
		conda install -yq $(CONDA_CHANNELS_OPT) --strict-channel-priority --file requirements.txt $(CONDA_ADDITIONAL_PACKAGES) && \
		$(CONDA_DEACTIVATE)

.PHONY: pypy-export-command
pypy-export-command:
	@echo $(PYPY_EXPORT_PYTHONPATH_CMD)

.PHONY: conda-activate-command
conda-activate-command:
	@echo 'conda activate $(CONDA_ENV); $(CONDA_POST_ACTIVATE)'

.PHONY: conda-deactivate-command
conda-deactivate-command:
	@echo conda deactivate

.PHONY: conda-clean
conda-clean:
	conda env remove -p $(CONDA_ENV)

.PHONY: clean
clean: test-clean coverage-clean conda-clean doc-clean dist-clean
	find youtube_playlist_downloader/ -name *.pyc -delete

################################## Run #########################################
RUN_OPTIONS := --format json --format default
ifdef PROFILE
RUN_OPTIONS := $(RUN_OPTIONS) --profile $(PROFILE)
endif
ifdef OUTFOLDER
RUN_OPTIONS := $(RUN_OPTIONS) --outfolder $(OUTFOLDER)
endif
.PHONY: run
run: validate test
	@echo "Running..."
	$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		$(PYTHON_CMD) $(PACKAGE_NAME) $(RUN_OPTIONS) $(SECRET_FILE) && \
		$(CONDA_DEACTIVATE)


############################### Style and Linting ##############################
# validates that style is conformant
.PHONY: validate-style
validate-style:
	@echo "Validating style..."
	$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		$(PYTHON_CMD) -m yapf -rd -e .vscode -e .conda_env_* . | tee >(cat >&2) | wc -w | xargs test  0 -eq && \
		$(CONDA_DEACTIVATE)

.PHONY: lint
lint:
	@echo "Linting..."
	$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		$(PYTHON_CMD) -m flake8 $(PACKAGE_NAME) && \
		$(CONDA_DEACTIVATE)

.PHONY: validate
validate: validate-style lint

############################ Tests and Coverage ################################

.PHONY: test
test:
	@echo "Running tests..."
	$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		$(PYTHON_CMD) -m pytest test && \
		$(CONDA_DEACTIVATE)


.PHONY: test-clean
test-clean:
	rm -rf credentials/pytest* out/pytest* .pytest-cache/
	find test/ -name *.pyc -delete

.PHONY: coverage-run
coverage-run:
	@echo "Running coverage..."
	$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		$(CPYTHON_BIN) -m coverage run --source $(PACKAGE_NAME) -m pytest test && \
		$(CONDA_DEACTIVATE)

.PHONY: coverage-percent
coverage-percent:
	@$(MAKE) coverage-run > /dev/null 2>&1
	@$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		$(CPYTHON_BIN) -m coverage json -o /dev/stdout \
		| jq .totals.percent_covered && \
		$(CONDA_DEACTIVATE)

.PHONY: coverage-test
coverage-test: COVERAGE_THRESHOLD := 75
coverage-test:
	$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		$(MAKE) -s --no-print-directory coverage-percent \
		| xargs echo "$(COVERAGE_THRESHOLD) <" \
		| bc | xargs test 0 -lt  && echo "Code coverage threshold met." \
		||  { echo "Code coverage is below $(COVERAGE_THRESHOLD)%." && false ; } && \
		$(CONDA_DEACTIVATE)

.PHONY: coverage-report
coverage-report: coverage-run
	@$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		$(CPYTHON_BIN) -m coverage json --pretty-print -o  coverage/coverage.json && \
		$(CPYTHON_BIN) -m coverage html -d coverage/html && \
		$(CPYTHON_BIN) -m coverage report | tee coverage/coverage.txt && \
		$(CONDA_DEACTIVATE)

.PHONY: coverage-clean
coverage-clean:
	rm -rf .coverage* coverage/*

################################ Documentation #################################
.PHONY: doc
doc:
	@$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		pdoc --html --force --config show_source_code=False -o doc $(PACKAGE_NAME) && \
		$(CONDA_DEACTIVATE)

.PHONY: doc-clean
doc-clean:
	rm -rf doc/

############################### Docker Targets #################################
.PHONY: docker-login
docker-login:
	docker login $(DOCKER_REGISTRY)

.PHONY: docker-build
docker-build:
	docker build -t $(DOCKER_REGISTRY)/$(DOCKER_IMAGE) .

.PHONY: docker-push
docker-push: docker-login docker-build
	docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE)

.PHONY: console
console:
	docker run --rm -it \
		-v $(CURDIR):/youtubeplaylistdownloader \
		-w /youtubeplaylistdownloader \
		$(DOCKER_REGISTRY)/$(DOCKER_IMAGE) || true
.PHONY: all
all: coverage doc run

################################ Deploy ########################################
.PHONY: dist
dist:
	@$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		python setup.py bdist_wheel && \
		$(CONDA_DEACTIVATE)

TWINE_OPTIONS := --disable-progress-bar
ifeq ($(DEPLOY_TEST), true)
TWINE_OPTIONS := $(TWINE_OPTIONS) --repository-url https://test.pypi.org/legacy/
endif

ifndef RELEASE_DESCRIPTION
ifeq ($(CI), true)
RELEASE_DESCRIPTION := $(CI_COMMIT_MESSAGE)
endif
endif

ifndef RELEASE_DESCRIPTION
RELEASE_DESCRIPTION := Release without details
endif

ifndef COMMIT_BRANCH
ifeq ($(CI), true)
COMMIT_BRANCH := $(shell echo $${CI_COMMIT_BRANCH:-master})
else
COMMIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
endif
endif
# Requires TWINE_USERNAME and TWINE_PASSWORD to be set
# Twine username could be '__token__' and password could be token
# Also requires GITLAB_PRIVATE_TOKEN be set
.PHONY: deploy
deploy: bump-version commit-version create-release deploy-pypi

.PHONY: deploy-pypi
deploy-pypi: dist
	$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		twine upload $(TWINE_OPTIONS) dist/* && \
		$(CONDA_DEACTIVATE)

.PHONY: dist-clean
dist-clean:
	rm -rf dist build *.egg-info

.PHONY: bump-version
bump-version:
	@$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		bump2version --allow-dirty --current-version $$(cat VERSION) patch VERSION && \
		$(CONDA_DEACTIVATE)

# Verify http response code  201
.PHONY: commit-version
commit-version:
	@echo "Updating version to $$(cat VERSION) and commiting to $(COMMIT_BRANCH) branch..."
	@$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		(($$(curl -s -o /dev/null -w '%{http_code}' --request POST \
		--header "PRIVATE-TOKEN: $(GITLAB_PRIVATE_TOKEN)" \
		--header "Content-Type: application/json" \
		--data '{"branch": "$(COMMIT_BRANCH)", "commit_message": "'"[skip ci] Auto update Version to $$(cat VERSION)"'", "actions": [{"action": "update", "file_path": "VERSION", "content": "'"$$(cat VERSION)"'"}]}' \
		"https://gitlab.com/api/v4/projects/$(GITLAB_PROJECT_ID)/repository/commits") == 201)) && \
		$(CONDA_DEACTIVATE)

create-release delete-release: RELEASE_NAME = $(shell echo $${RELEASE_NAME:-v$$(cat VERSION)})
.PHONY: create-release
# RELEASE_DESCRIPTION could be multi-line string.
# Expanding in the bash avoids special handling in Makefile
create-release:
	@echo "Creating release $(RELEASE_NAME)..."
	@$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		data="$$(jq -nc --arg relelase_name "$(RELEASE_NAME)" --arg release_description "$${RELEASE_DESCRIPTION}" '{ "name": $$relelase_name, "ref": "$(COMMIT_BRANCH)", "tag_name": $$relelase_name, "description": $$release_description }')" && \
		(($$(curl -s -o /dev/null -w '%{http_code}' \
		--header 'Content-Type: application/json' \
		--header "PRIVATE-TOKEN: $(GITLAB_PRIVATE_TOKEN)" \
		--data "$${data}" \
		--request POST "https://gitlab.com/api/v4/projects/$(GITLAB_PROJECT_ID)/releases") == 201)) && \
		$(CONDA_DEACTIVATE)

.PHONY: delete-release
delete-release:
	@echo "Deleting release $(RELEASE_NAME)..."
	@$(CONDA_ACTIVATE) && $(CONDA_POST_ACTIVATE) && \
		(($$(curl -s -o /dev/null -w '%{http_code}' --request DELETE \
		--header "PRIVATE-TOKEN: $(GITLAB_PRIVATE_TOKEN)" \
		"https://gitlab.com/api/v4/projects/$(GITLAB_PROJECT_ID)/releases/$(RELEASE_NAME)") == 200)) && \
		$(CONDA_DEACTIVATE)
	@git push --delete origin $(RELEASE_NAME) && git fetch -pP
