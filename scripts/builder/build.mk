.PHONY: build

BUILD_TIMESTAMP = $(TIMESTAMP_DIR)/.build.stamp

build: $(TIMESTAMP_DIR) development--install poetry--update build--python ## Complete project install and build artifacts for deployment

clean: poetry--clean ## Complete clear-out of the project installation and artifacts
	[[ -d $(TIMESTAMP_DIR) ]] && rm -r $(TIMESTAMP_DIR) || :

build--python: $(BUILD_TIMESTAMP)  ## Builds local python packages into .zip files

$(BUILD_TIMESTAMP): $(TIMESTAMP_DIR) $(shell find src -type f -name "*.py" -not -path "*/test_*" -not -path "*/dist/*" )
	@find $(CURDIR) -name make.py | xargs -I % bash -c 'poetry run python %'
	touch $(BUILD_TIMESTAMP)
