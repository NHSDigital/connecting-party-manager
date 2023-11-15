.PHONY: development--install

PATH_TO_DEPS = $(CURDIR)/scripts/local-development
TOOL_VERSIONS = $(CURDIR)/.tool-versions
TOOL_TIMESTAMP = $(TIMESTAMP_DIR)/tool-versions.stamp

development--install: $(TOOL_TIMESTAMP) ## Install local development tools

$(TOOL_TIMESTAMP): $(TIMESTAMP_DIR) $(TOOL_VERSIONS)
	@bash $(PATH_TO_DEPS)/install.sh
	touch $(TOOL_TIMESTAMP)

# $(TOOL_VERSIONS):
# 	touch $(TOOL_VERSIONS)
