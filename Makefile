MAKEFLAGS += --silent
SHELL = bash
.DEFAULT_GOAL := help
.PHONY: help

PROJECT_PREFIX = "nhse-cpm-"
TIMESTAMP_DIR = $(CURDIR)/.timestamp
AWS_DEFAULT_REGION ?= "eu-west-2"
DOWNLOADS_DIR = $(CURDIR)/.downloads
PATH_TO_INFRASTRUCTURE = $(CURDIR)/scripts/infrastructure

INIT_TIMESTAMP = $(CURDIR)/.timestamp/init.timestamp


include scripts/**/*.mk

help:  ## This help message
	@grep -E --no-filename '^[a-zA-Z-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-42s\033[0m %s\n", $$1, $$2}'

$(INIT_TIMESTAMP):
	@mkdir -p $(TIMESTAMP_DIR)
	@mkdir -p $(DOWNLOADS_DIR)
	touch $(INIT_TIMESTAMP)
