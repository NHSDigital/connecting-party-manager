.PHONY: development--install

PATH_TO_DEPS = $(CURDIR)/scripts/local-development
TOOL_VERSIONS = .tool-versions
TOOL_TIMESTAMP = $(TIMESTAMP_DIR)/$(TOOL_VERSIONS).stamp

development--install: $(TOOL_TIMESTAMP) ## Install local development tools

$(TOOL_TIMESTAMP): $(TIMESTAMP_DIR) $(TOOL_VERSIONS)
	@bash $(PATH_TO_DEPS)/install.sh
	touch $(TOOL_TIMESTAMP)