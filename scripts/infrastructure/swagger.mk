.PHONY: swagger--merge swagger--clean swagger--download-generator

SWAGGER_GENERATOR_VERSION = 4.6.1
SWAGGER_GENERATOR_JAR = fhir-swagger-generator-$(SWAGGER_GENERATOR_VERSION)-cli.jar
PATH_TO_SWAGGER_GENERATOR_JAR := $(DOWNLOADS_DIR)/$(SWAGGER_GENERATOR_JAR)

FHIR_DEFINITION = $(CURDIR)/infrastructure/swagger/swagger-fhir-generator-definitions/endpoints.yaml

FHIR_BASE_TIMESTAMP =  $(TIMESTAMP_DIR)/.fhir-base.stamp
SWAGGER_DIST = $(CURDIR)/infrastructure/swagger/dist
SWAGGER_FHIR_BASE = $(SWAGGER_DIST)/fhir-base
SWAGGER_AWS = $(SWAGGER_DIST)/aws/swagger.yaml
SWAGGER_PUBLIC = $(SWAGGER_DIST)/public/swagger.yaml
SWAGGER_APIGEE = $(SWAGGER_DIST)/apigee/swagger.yaml

swagger--merge: $(SWAGGER_AWS) $(SWAGGER_PUBLIC) $(SWAGGER_APIGEE) ## Updates swagger builds from the components in the infrastructure/swagger/ directory.
swagger--clean:  ## Removes swagger builds.
	[[ -f $(FHIR_BASE_TIMESTAMP) ]] && rm $(FHIR_BASE_TIMESTAMP) || :
	[[ -d $(SWAGGER_DIST) ]] && rm -r $(SWAGGER_DIST) || :
	[[ -f $(PATH_TO_SWAGGER_GENERATOR_JAR) ]] && rm $(PATH_TO_SWAGGER_GENERATOR_JAR) || :
swagger--generate-fhir-base: $(FHIR_BASE_TIMESTAMP)
swagger--download-generator: $(PATH_TO_SWAGGER_GENERATOR_JAR)  ## Downloads the latest swagger fhir generator


$(PATH_TO_SWAGGER_GENERATOR_JAR): $(DOWNLOADS_DIR)
	@echo "Downloading FHIR Swagger Generator to $(DOWNLOADS_DIR)"
	@wget -q https://github.com/IBM/FHIR/releases/download/$(SWAGGER_GENERATOR_VERSION)/$(SWAGGER_GENERATOR_JAR) -P $(DOWNLOADS_DIR)
	touch $(PATH_TO_SWAGGER_GENERATOR_JAR)


$(FHIR_BASE_TIMESTAMP): $(PATH_TO_SWAGGER_GENERATOR_JAR) $(FHIR_DEFINITION) ## Generate the FHIR base swagger from the definitions file
	mkdir -p $(SWAGGER_FHIR_BASE)
	@env \
		PATH_TO_FHIR_DEFINITIONS=$(FHIR_DEFINITION) \
		PATH_TO_SWAGGER_GENERATOR_JAR=$(PATH_TO_SWAGGER_GENERATOR_JAR) \
		SWAGGER_FHIR_BASE=$(SWAGGER_FHIR_BASE) \
		bash $(PATH_TO_INFRASTRUCTURE)/swagger/fhir-swagger-generator.sh
	touch $(FHIR_BASE_TIMESTAMP)

$(SWAGGER_AWS): $(FHIR_BASE_TIMESTAMP) $(shell find infrastructure/swagger -type f -name "*.yaml" -not -path "*/dist/*.yaml" )
	@env MERGE_AWS=1 bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh
	npx --yes @redocly/cli lint $(SWAGGER_AWS) --skip-rule operation-4xx-response --skip-rule spec-components-invalid-map-name || ([[ -f $(FHIR_BASE_TIMESTAMP) ]] && rm $(FHIR_BASE_TIMESTAMP) || :; exit 1)
	touch $(SWAGGER_AWS)

$(SWAGGER_PUBLIC): $(FHIR_BASE_TIMESTAMP) $(shell find infrastructure/swagger -type f -name "*.yaml" -not -path "*/dist/*.yaml" )
	@env MERGE_PUBLIC=1 bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh
	npx --yes @redocly/cli lint $(SWAGGER_PUBLIC) --skip-rule security-defined || ([[ -f $(FHIR_BASE_TIMESTAMP) ]] && rm $(FHIR_BASE_TIMESTAMP) || :; exit 1)
	touch $(SWAGGER_PUBLIC)

$(SWAGGER_APIGEE): $(FHIR_BASE_TIMESTAMP) $(shell find infrastructure/swagger -type f -name "*.yaml" -not -path "*/dist/*.yaml" )
	@env MERGE_APIGEE=1 bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh
	npx --yes @redocly/cli lint $(SWAGGER_APIGEE) --skip-rule security-defined || ([[ -f $(FHIR_BASE_TIMESTAMP) ]] && rm $(FHIR_BASE_TIMESTAMP) || :; exit 1)
	touch $(SWAGGER_APIGEE)
