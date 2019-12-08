SHELL := bash
PROFILE ?= krunalnsoni

.PHONY: setup
setup:
	pip3 install -U -r requirements.txt 

# validates that style is conformant
.PHONY: validate-style
validate-style:
	@(yapf -rd -e .vscode . | wc -l | xargs test  0 -eq) && true

.PHONY: lint
lint:
	flake8 youtube-playlist-downloader

.PHONY: validate lint
validate: validate-style

.PHONY: run
run: validate
	python3 youtube-playlist-downloader --profile $(PROFILE)

.PHONY: test
test:
	@true