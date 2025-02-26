.PHONY: build

BUILD_TIMESTAMP = $(TIMESTAMP_DIR)/.build.timestamp
POSTMAN_COLLECTION = $(CURDIR)/src/api/tests/feature_tests/postman-collection.json

TOOL_VERSIONS_COPY = $(TIMESTAMP_DIR)/tool-versions.copy
POETRY_LOCK = $(CURDIR)/poetry.lock
INIT_TIMESTAMP = $(CURDIR)/.timestamp/init.timestamp
SRC_FILES = $(shell find src/api src/layers src/test_helpers -type f -name "*.py" -not -path "*/feature_tests/*" -not -path "*/test_*" -not -path "*/fhir/r4/strict_models.py" -not -path "*/fhir/r4/models.py" -not -path "*/archived_epr/*")
THIRD_PARTY_DIST = $(CURDIR)/src/layers/third_party/dist
SWAGGER_DIST = $(CURDIR)/infrastructure/swagger/dist
SWAGGER_PUBLIC = $(SWAGGER_DIST)/public/swagger.yaml
SWAGGER_AWS = $(SWAGGER_DIST)/aws/swagger.yaml

BUILD_DEPENDENCIES = $(INIT_TIMESTAMP) \
										 $(SRC_FILES) \
										 $(TOOL_VERSIONS_COPY) \
										 $(POETRY_LOCK) \
										 $(SWAGGER_PUBLIC) \
										 $(SWAGGER_AWS)


clean: poetry--clean swagger--clean terraform--clean ## Complete clear-out of the project installation and artifacts
	[[ -d $(TIMESTAMP_DIR) ]] && rm -r $(TIMESTAMP_DIR) || :
	[[ -d $(DOWNLOADS_DIR) ]] && rm -r $(DOWNLOADS_DIR) || :
	[[ -d $(THIRD_PARTY_DIST) ]] && rm -r $(THIRD_PARTY_DIST) || :
	[[ -f $(POSTMAN_COLLECTION) ]] && rm $(POSTMAN_COLLECTION) || :

clean--build:
	[[ -f $(BUILD_TIMESTAMP) ]] && rm $(BUILD_TIMESTAMP) || :

build: $(BUILD_TIMESTAMP) ## Complete project install and build artifacts for deployment

$(BUILD_TIMESTAMP): $(BUILD_DEPENDENCIES)
	@find $(CURDIR)/src -name make.py | xargs -n 1 -P 8 -I % bash -c 'poetry run python %'
	touch $(BUILD_TIMESTAMP)

generate--sbom: build
	syft ./ -o cyclonedx-json@1.5=cpm.cdx.json

validate--sbom: generate--sbom
	grype sbom:./cpm.cdx.json --fail-on CRITICAL

timestamp--reset:
	@if [ -z "$(FILEPATH)" ]; then \
		echo "Error: FILEPATH not provided"; \
		exit 1; \
	fi
	FILEPATH=$(FILEPATH) bash $(CURDIR)/scripts/builder/timestamp_reset.sh
