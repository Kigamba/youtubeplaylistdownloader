DOCKER_REGISTRY ?= registry.gitlab.com
DOCKER_IMAGE ?= planetsoni/youtubeplaylistdownloader

# This project supports both cpython and pypy
# choose cpython or pypy
PYTHON_IMP ?= cpython
CPYTHON_VERSION ?= 3.7
CPYTHON_BIN := python

PYPY_VERSION ?= 3.5
PYPY_BIN := pypy3

# options for running
SECRET_FILE ?= 
PROFILE ?=
OUTFOLDER ?=

# options for deploying
DEPLOY_TEST ?= true
CI ?= false
export RELEASE_DESCRIPTION ?=
RELEASE_NAME ?=
GITLAB_PROJECT_ID := 15751804
TWINE_USERNAME ?=
TWINE_PASSWORD ?=
GITLAB_PRIVATE_TOKEN ?=
COMMIT_BRANCH ?=
