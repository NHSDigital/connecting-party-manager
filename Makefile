MAKEFLAGS += --silent
SHELL = bash
.DEFAULT_GOAL := help
.PHONY: help

include scripts/**/*.mk

help:  ## This help message
	@grep -E --no-filename '^[a-zA-Z-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-42s\033[0m %s\n", $$1, $$2}'
