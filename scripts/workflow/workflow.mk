.PHONY: workflow--create-release-branch workflow--check--rebased-on-main workflow--check--branch-name workflow--precommit-run-all

PATH_TO_WORKFLOW := $(CURDIR)/scripts/workflow
JIRA_TICKET :=
DESCRIPTION :=
MESSAGE :=

workflow--create-release-branch: workflow--check--rebased-on-main ## Create a release branch based on the current date
	@bash $(PATH_TO_WORKFLOW)/create-release-branch.sh

workflow--check--rebased-on-main:  ## Check that the current branch is rebased on origin/main
	@bash $(PATH_TO_WORKFLOW)/check-rebased-on-main.sh

workflow--check--branch-name:  ## Check the branch name format
	@bash $(PATH_TO_WORKFLOW)/check-branch-name.sh

workflow--check--release-branch-name:  ## Check the release branch name format
	@bash $(PATH_TO_WORKFLOW)/check-release-branch-name.sh

workflow--create-feature-branch: workflow--check--rebased-on-main  ## Create a feature branch. Must provide JIRA_TICKET and DESCRIPTION keyword arguments.
	@if [ -z "$(JIRA_TICKET)" ] || [ -z "$(DESCRIPTION)" ]; then \
		echo "Error: Both JIRA_TICKET and DESCRIPTION must be provided."; \
		exit 1; \
	fi
	@bash $(PATH_TO_WORKFLOW)/create-feature-branch.sh $(JIRA_TICKET) "$(DESCRIPTION)"

workflow--create-changelog: workflow--check--release-branch-name  ## Create a changelog file for this release
	@bash $(PATH_TO_WORKFLOW)/create-changelog.sh

workflow--create-release-commit: ## The initial commit for this release
	@bash $(PATH_TO_WORKFLOW)/create-release-commit.sh

workflow--commit: ## Format the the commit message with [branch-name] <message> using MESSAGE="<message>"
	@if [ -z "$(MESSAGE)" ]; then \
		echo "Error: MESSAGE must be provided."; \
		exit 1; \
	fi
	@MESSAGE="$(MESSAGE)" bash $(PATH_TO_WORKFLOW)/commit.sh

workflow--codebase-checks:  ## Runs all codebase checks (lint, changelog, etc)
	.venv/bin/pre-commit run --all-files
