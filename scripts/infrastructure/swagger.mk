.PHONY: swagger--merge swagger--clean swagger--download-generator

SWAGGER_GENERATOR_VERSION = 4.6.1
SWAGGER_GENERATOR_JAR = fhir-swagger-generator-$(SWAGGER_GENERATOR_VERSION)-cli.jar
PATH_TO_SWAGGER_GENERATOR_JAR := $(DOWNLOADS_DIR)/$(SWAGGER_GENERATOR_JAR)

FHIR_DEFINITION = $(CURDIR)/infrastructure/swagger/swagger-fhir-generator-definitions/endpoints.yaml
WORKSPACE_OUTPUT_JSON = $(CURDIR)/infrastructure/terraform/per_workspace/output.json
VENV_PYTHON = $(CURDIR)/.venv/bin/python
INIT_TIMESTAMP = $(CURDIR)/.timestamp/init.timestamp

FHIR_BASE_TIMESTAMP =  $(TIMESTAMP_DIR)/.fhir-base.stamp
SWAGGER_DIST = $(CURDIR)/infrastructure/swagger/dist
SWAGGER_FHIR_BASE = $(SWAGGER_DIST)/fhir-base
SWAGGER_AWS = $(SWAGGER_DIST)/aws/swagger.yaml
SWAGGER_PUBLIC = $(SWAGGER_DIST)/public/swagger.yaml
SWAGGER_APIGEE = $(SWAGGER_DIST)/apigee/swagger.yaml
_CLEANED_SWAGGER_FILE = $(SWAGGER_DIST)/build/_02_clean.yaml
PROXYGEN_TIMESTAMP = $(TIMESTAMP_DIR)/.proxygen.stamp
SWAGGER_PUBLISH_TIMESTAMP = $(TIMESTAMP_DIR)/.swagger.publish.stamp

TOOL_VERSIONS_COPY = $(TIMESTAMP_DIR)/tool-versions.copy
SWAGGER_DEPENDENCIES = $(FHIR_BASE_TIMESTAMP) $(shell find infrastructure/swagger -type f -name "*.yaml" -not -path "*/dist/*.yaml" ) $(shell find scripts/infrastructure/swagger -type f -name "*.sh") $(TOOL_VERSIONS_COPY)

swagger--merge--aws: $(SWAGGER_AWS) ## Updates API Gateway swagger builds from the components in the infrastructure/swagger/ directory.
swagger--merge--public: $(SWAGGER_PUBLIC) ## Updates public swagger builds from the components in the infrastructure/swagger/ directory.
swagger--merge--apigee: $(SWAGGER_APIGEE) ## Updates Apigee swagger builds from the components in the infrastructure/swagger/ directory.
swagger--clean:  ## Removes swagger builds.
	[[ -f $(FHIR_BASE_TIMESTAMP) ]] && rm $(FHIR_BASE_TIMESTAMP) || :
	[[ -d $(SWAGGER_DIST) ]] && rm -r $(SWAGGER_DIST) || :
	[[ -f $(PATH_TO_SWAGGER_GENERATOR_JAR) ]] && rm $(PATH_TO_SWAGGER_GENERATOR_JAR) || :
swagger--generate-fhir-base: $(FHIR_BASE_TIMESTAMP)
swagger--download-generator: $(PATH_TO_SWAGGER_GENERATOR_JAR)  ## Downloads the latest swagger fhir generator
swagger--publish: $(SWAGGER_PUBLISH_TIMESTAMP) ## Publish swagger docs via proxygen to API Catalogue



$(PATH_TO_SWAGGER_GENERATOR_JAR): $(INIT_TIMESTAMP)
	@echo "Downloading FHIR Swagger Generator to $(DOWNLOADS_DIR)"
	@wget -q https://github.com/IBM/FHIR/releases/download/$(SWAGGER_GENERATOR_VERSION)/$(SWAGGER_GENERATOR_JAR) -P $(DOWNLOADS_DIR)
	touch $(PATH_TO_SWAGGER_GENERATOR_JAR)


$(FHIR_BASE_TIMESTAMP): $(INIT_TIMESTAMP) $(VENV_PYTHON) $(PATH_TO_SWAGGER_GENERATOR_JAR) $(FHIR_DEFINITION) ## Generate the FHIR base swagger from the definitions file
	mkdir -p $(SWAGGER_FHIR_BASE)
	@env \
		PATH_TO_FHIR_DEFINITIONS=$(FHIR_DEFINITION) \
		PATH_TO_SWAGGER_GENERATOR_JAR=$(PATH_TO_SWAGGER_GENERATOR_JAR) \
		SWAGGER_FHIR_BASE=$(SWAGGER_FHIR_BASE) \
		bash $(PATH_TO_INFRASTRUCTURE)/swagger/fhir-swagger-generator.sh
	touch $(FHIR_BASE_TIMESTAMP)

$(_CLEANED_SWAGGER_FILE): $(FHIR_BASE_TIMESTAMP) $(SWAGGER_DEPENDENCIES)
	@env bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh merge_base || ([[ -f $(FHIR_BASE_TIMESTAMP) ]] && rm $(FHIR_BASE_TIMESTAMP) || :; exit 1)


$(SWAGGER_AWS): $(SWAGGER_DEPENDENCIES) $(_CLEANED_SWAGGER_FILE)
	@env bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh generate_aws_swagger
	npx --yes @redocly/cli lint $(SWAGGER_AWS) --skip-rule operation-4xx-response --skip-rule spec-components-invalid-map-name || ([[ -f $(FHIR_BASE_TIMESTAMP) ]] && rm $(FHIR_BASE_TIMESTAMP) || :; exit 1)

$(SWAGGER_PUBLIC): $(SWAGGER_DEPENDENCIES) $(_CLEANED_SWAGGER_FILE)
	@env bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh generate_public_swagger
	npx --yes @redocly/cli lint $(SWAGGER_PUBLIC) --skip-rule security-defined || ([[ -f $(FHIR_BASE_TIMESTAMP) ]] && rm $(FHIR_BASE_TIMESTAMP) || :; exit 1)

$(SWAGGER_APIGEE): $(SWAGGER_DEPENDENCIES) $(_CLEANED_SWAGGER_FILE) $(WORKSPACE_OUTPUT_JSON)
	@env bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh generate_apigee_swagger
	npx --yes @redocly/cli lint $(SWAGGER_APIGEE) --skip-rule security-defined || ([[ -f $(FHIR_BASE_TIMESTAMP) ]] && rm $(FHIR_BASE_TIMESTAMP) || :; exit 1)

$(SWAGGER_PUBLISH_TIMESTAMP): aws--login $(SWAGGER_PUBLIC) $(WORKSPACE_OUTPUT_JSON)
	[[ -f $(SWAGGER_PUBLISH_TIMESTAMP) ]] && rm $(SWAGGER_PUBLISH_TIMESTAMP) || :

	WORKSPACE_OUTPUT_JSON=$(WORKSPACE_OUTPUT_JSON) \
	ENVIRONMENT_MAPPING_YAML=$(ENVIRONMENT_MAPPING_YAML) \
	STAGE_MAPPING_YAML=$(STAGE_MAPPING_YAML) \
	APIGEE_CONFIG_PATH=$(APIGEE_CONFIG_PATH) \
	SWAGGER_APIGEE=$(SWAGGER_APIGEE) \
	SWAGGER_PUBLIC=$(SWAGGER_PUBLIC) \
	AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		bash $(PATH_TO_INFRASTRUCTURE)/apigee/proxygen.sh publish_swagger
