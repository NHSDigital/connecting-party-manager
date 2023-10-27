.PHONY: build

BUILD_TIMESTAMP = $(TIMESTAMP_DIR)/.build.stamp

clean: poetry--clean swagger--clean ## Complete clear-out of the project installation and artifacts
	[[ -d $(TIMESTAMP_DIR) ]] && rm -r $(TIMESTAMP_DIR) || :

clean--build:
	[[ -f $(BUILD_TIMESTAMP) ]] && rm $(BUILD_TIMESTAMP) || :

build: $(TIMESTAMP_DIR) development--install poetry--update build--python swagger--merge ## Complete project install and build artifacts for deployment

build--python: $(BUILD_TIMESTAMP)  ## Builds local python packages into .zip files

build--python--force: clean--build $(BUILD_TIMESTAMP)  ## Force a rebuild of local python packages into .zip files

$(BUILD_TIMESTAMP): $(TIMESTAMP_DIR) $(shell find src -type f -name "*.py" -not -path "*/test_*" )
	@find $(CURDIR) -name make.py | xargs -I % bash -c 'poetry run python %'
	touch $(BUILD_TIMESTAMP)
