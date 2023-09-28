.PHONY: build

build: $(TIMESTAMP_DIR) development--install poetry--update ## Complete project install and build artifacts of for deployment
	@echo "build"

clean: poetry--clean ## Complete clear-out of the project installation and artifacts
	[[ -d $(TIMESTAMP_DIR) ]] && rm -r $(TIMESTAMP_DIR) || :
