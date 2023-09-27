.PHONY: workflow--create-release-branch workflow--check--rebased-on-main workflow--check--branch-name workflow--precommit-run-all

PATH_TO_HERE := $(CURDIR)/scripts/workflow

workflow--create-release-branch:  ## Create a release branch based on the current date
	@bash $(PATH_TO_HERE)/create-release-branch.sh

workflow--check--rebased-on-main:  ## Check that the current branch is rebased on origin/main
	@bash $(PATH_TO_HERE)/check-rebased-on-main.sh

workflow--check--branch-name:  ## Check the release branch name format
	@bash $(PATH_TO_HERE)/check-branch-name.sh

workflow--precommit-run-all:  ## Runs all pre-commit hooks (lint, changelog, etc)
	.venv/bin/pre-commit run --all-files
