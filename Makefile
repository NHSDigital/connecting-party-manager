MAKEFLAGS += --silent
SHELL = bash
.DEFAULT_GOAL := help
.PHONY: help

PROJECT_PREFIX = "nhse-cpm-"
TIMESTAMP_DIR := .timestamp

include scripts/**/*.mk

help:  ## This help message
	@grep -E --no-filename '^[a-zA-Z-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-42s\033[0m %s\n", $$1, $$2}'

$(TIMESTAMP_DIR):
	@mkdir $(TIMESTAMP_DIR)
