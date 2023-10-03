.PHONY: changelog--get-latest-release

changelog--get-latest-release:  ## Print the latest release from the CHANGELOG
	@bash $(CURDIR)/scripts/changelog/get-latest-release.sh
