.PHONY: development--install

PATH_TO_DEPS = $(CURDIR)/scripts/local-development
TIMESTAMP_DIR = $(CURDIR)/.timestamp
TOOL_VERSIONS = $(CURDIR)/.tool-versions
TOOL_VERSIONS_COPY = $(TIMESTAMP_DIR)/tool-versions.copy

development--install: $(TOOL_VERSIONS_COPY) ## Install local development tools

## NEED TO ADD A PROXY TO TOOL_VERSIONS HERE, WHICH CHECKS FOR CONTENT CHANGES

$(TOOL_VERSIONS_COPY): $(TOOL_VERSIONS)
	touch $(TOOL_VERSIONS_COPY)
	diff -q $(TOOL_VERSIONS_COPY) $(TOOL_VERSIONS) || exit 0
	@bash $(PATH_TO_DEPS)/install.sh
	cp $(TOOL_VERSIONS) $(TOOL_VERSIONS_COPY)
