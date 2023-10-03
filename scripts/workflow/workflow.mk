.PHONY: workflow--create-release-branch workflow--check--rebased-on-main workflow--check--branch-name workflow--precommit-run-all

PATH_TO_HERE := $(CURDIR)/scripts/workflow
JIRA_TICKET :=
DESCRIPTION :=

workflow--create-release-branch: workflow--check--rebased-on-main ## Create a release branch based on the current date
	@bash $(PATH_TO_HERE)/create-release-branch.sh

workflow--check--rebased-on-main:  ## Check that the current branch is rebased on origin/main
	@bash $(PATH_TO_HERE)/check-rebased-on-main.sh

workflow--check--branch-name:  ## Check the branch name format
	@bash $(PATH_TO_HERE)/check-branch-name.sh

workflow--create-feature-branch: workflow--check--rebased-on-main  ## Create a feature branch. Must provide JIRA_TICKET and DESCRIPTION keyword arguments.
	@if [ -z "$(JIRA_TICKET)" ] || [ -z "$(DESCRIPTION)" ]; then \
		echo "Error: Both JIRA_TICKET and DESCRIPTION must be provided."; \
		exit 1; \
	fi
	@bash $(PATH_TO_HERE)/create-feature-branch.sh $(JIRA_TICKET) "$(DESCRIPTION)"


workflow--codebase-checks:  ## Runs all codebase checks (lint, changelog, etc)
	.venv/bin/pre-commit run --all-files
