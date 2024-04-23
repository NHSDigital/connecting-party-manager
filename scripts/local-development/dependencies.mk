.PHONY: development--install

PATH_TO_DEPS = $(CURDIR)/scripts/local-development
TIMESTAMP_DIR = $(CURDIR)/.timestamp
TOOL_VERSIONS = $(CURDIR)/.tool-versions
TOOL_VERSIONS_COPY = $(TIMESTAMP_DIR)/tool-versions.copy
INIT_TIMESTAMP = $(CURDIR)/.timestamp/init.timestamp

development--install: $(TOOL_VERSIONS_COPY) ## Install local development tools

$(TOOL_VERSIONS_COPY): $(INIT_TIMESTAMP) $(TOOL_VERSIONS)
	touch $(TOOL_VERSIONS_COPY)
	diff -q $(TOOL_VERSIONS_COPY) $(TOOL_VERSIONS) || exit 0
	@bash $(PATH_TO_DEPS)/install.sh
	cp $(TOOL_VERSIONS) $(TOOL_VERSIONS_COPY)
