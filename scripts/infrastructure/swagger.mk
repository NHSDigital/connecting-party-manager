.PHONY: swagger--merge swagger--clean swagger--download-generator

SWAGGER_GENERATOR_VERSION = 4.6.1
SWAGGER_GENERATOR_JAR = fhir-swagger-generator-$(SWAGGER_GENERATOR_VERSION)-cli.jar
PATH_TO_SWAGGER_GENERATOR_JAR := $(CURDIR)/$(DOWNLOADS_DIR)/$(SWAGGER_GENERATOR_JAR)

FHIR_DEFINITION = $(CURDIR)/infrastructure/swagger/swagger-fhir-generator-definitions/config.yaml

SWAGGER_TIMESTAMP = $(TIMESTAMP_DIR)/.swagger.stamp
SWAGGER_DIST = $(CURDIR)/infrastructure/swagger/dist
SWAGGER_FHIR_BASE = $(SWAGGER_DIST)/fhir-base
SWAGGER_AWS = $(SWAGGER_DIST)/aws/swagger.yaml
SWAGGER_PUBLIC = $(SWAGGER_DIST)/public/swagger.yaml

swagger--merge: $(SWAGGER_AWS) $(SWAGGER_PUBLIC) ## Updates swagger builds from the components in the infrastructure/swagger/ directory.
swagger--clean:  ## Removes swagger builds.
	[[ -f $(SWAGGER_TIMESTAMP) ]] && rm $(SWAGGER_TIMESTAMP) || :
	[[ -d $(SWAGGER_DIST) ]] && rm -r $(SWAGGER_DIST) || :
	[[ -f $(PATH_TO_SWAGGER_GENERATOR_JAR) ]] && rm $(PATH_TO_SWAGGER_GENERATOR_JAR) || :
swagger--download-generator: $(PATH_TO_SWAGGER_GENERATOR_JAR)  ## Downloads the latest swagger fhir generator
swagger--generate-fhir-base: $(SWAGGER_FHIR_BASE)  ## Generate the FHIR base swagger from the definitions file

$(PATH_TO_SWAGGER_GENERATOR_JAR): $(DOWNLOADS_DIR)
	@echo "Downloading FHIR Swagger Generator to $(DOWNLOADS_DIR)"
	@wget -q https://github.com/IBM/FHIR/releases/download/$(SWAGGER_GENERATOR_VERSION)/$(SWAGGER_GENERATOR_JAR) -P $(DOWNLOADS_DIR)
	touch $(PATH_TO_SWAGGER_GENERATOR_JAR)

$(SWAGGER_FHIR_BASE): $(PATH_TO_SWAGGER_GENERATOR_JAR) $(FHIR_DEFINITION)
	mkdir -p $(SWAGGER_FHIR_BASE)
	@env \
		PATH_TO_FHIR_DEFINITIONS=$(FHIR_DEFINITION) \
		PATH_TO_SWAGGER_GENERATOR_JAR=$(PATH_TO_SWAGGER_GENERATOR_JAR) \
		SWAGGER_FHIR_BASE=$(SWAGGER_FHIR_BASE) \
		bash $(PATH_TO_INFRASTRUCTURE)/swagger/fhir-swagger-generator.sh
	touch $(SWAGGER_FHIR_BASE)

$(SWAGGER_DIST)/%/swagger.yaml: $(SWAGGER_TIMESTAMP) $(SWAGGER_FHIR_BASE) $(REDOCLY) $(shell find infrastructure/swagger -type f -name "*.yaml" -not -path "*/dist/*.yaml" )
	@bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh

	npx --yes @redocly/cli lint $(SWAGGER_AWS) --skip-rule operation-4xx-response --skip-rule spec-components-invalid-map-name || ([[ -f $(SWAGGER_TIMESTAMP) ]] && rm $(SWAGGER_TIMESTAMP) || :; exit 1)
	touch $(SWAGGER_AWS)

	npx --yes @redocly/cli lint $(SWAGGER_PUBLIC) --skip-rule security-defined || ([[ -f $(SWAGGER_TIMESTAMP) ]] && rm $(SWAGGER_TIMESTAMP) || :; exit 1)
	touch $(SWAGGER_PUBLIC)


$(SWAGGER_TIMESTAMP): $(TIMESTAMP_DIR)
	touch $(SWAGGER_TIMESTAMP)
