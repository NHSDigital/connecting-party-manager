PATH_TO_HERE := $(CURDIR)/scripts/local-development

.PHONY: development--install

development--install:
	@bash $(PATH_TO_HERE)/install.sh
