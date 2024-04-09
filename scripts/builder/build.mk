.PHONY: build

BUILD_TIMESTAMP = $(TIMESTAMP_DIR)/.build.timestamp
POSTMAN_COLLECTION = $(CURDIR)/src/api/tests/feature_tests/postman-collection.json

TOOL_VERSIONS_COPY = $(TIMESTAMP_DIR)/tool-versions.copy
POETRY_LOCK = $(CURDIR)/poetry.lock
INIT_TIMESTAMP = $(CURDIR)/.timestamp/init.timestamp
SRC_FILES = $(shell find src -type f -name "*.py" -not -path "*/test_*" -not -path "*/fhir/r4/strict_models.py" -not -path "*/fhir/r4/models.py")
THIRD_PARTY_DIST = $(CURDIR)/src/layers/third_party/dist
SWAGGER_DIST = $(CURDIR)/infrastructure/swagger/dist
SWAGGER_PUBLIC = $(SWAGGER_DIST)/public/swagger.yaml
SWAGGER_AWS = $(SWAGGER_DIST)/aws/swagger.yaml
FHIR_MODEL_PATH = $(CURDIR)/src/layers/domain/fhir/r4
NORMAL_MODEL_PATH = $(FHIR_MODEL_PATH)/models.py
STRICT_MODEL_PATH = $(FHIR_MODEL_PATH)/strict_models.py

BUILD_DEPENDENCIES = $(INIT_TIMESTAMP) \
					 $(SRC_FILES) \
				     $(TOOL_VERSIONS_COPY) \
					 $(POETRY_LOCK) \
					 $(SWAGGER_PUBLIC) \
					 $(SWAGGER_AWS) \
					 $(NORMAL_MODEL_PATH) \
					 $(STRICT_MODEL_PATH)


clean: poetry--clean swagger--clean fhir--models--clean terraform--clean ## Complete clear-out of the project installation and artifacts
	[[ -d $(TIMESTAMP_DIR) ]] && rm -r $(TIMESTAMP_DIR) || :
	[[ -d $(DOWNLOADS_DIR) ]] && rm -r $(DOWNLOADS_DIR) || :
	[[ -d $(THIRD_PARTY_DIST) ]] && rm -r $(THIRD_PARTY_DIST) || :
	[[ -f $(POSTMAN_COLLECTION) ]] && rm $(POSTMAN_COLLECTION) || :

clean--build:
	[[ -f $(BUILD_TIMESTAMP) ]] && rm $(BUILD_TIMESTAMP) || :

build: $(BUILD_TIMESTAMP) ## Complete project install and build artifacts for deployment

$(BUILD_TIMESTAMP): $(BUILD_DEPENDENCIES)
	@find $(CURDIR) -name make.py | xargs -I % bash -c 'poetry run python %'
	touch $(BUILD_TIMESTAMP)
