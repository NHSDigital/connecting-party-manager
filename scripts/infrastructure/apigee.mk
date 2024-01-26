.PHONY: apigee--deploy apigee--clean

APIGEE_CONFIG_PATH = $(CURDIR)/infrastructure/apigee
APIGEE_TIMESTAMP = $(TIMESTAMP_DIR)/.apigee.stamp
PROXYGEN_TIMESTAMP = $(TIMESTAMP_DIR)/.proxygen.stamp

SWAGGER_APIGEE = $(SWAGGER_DIST)/apigee/swagger.yaml
WORKSPACE_OUTPUT_JSON = $(CURDIR)/infrastructure/terraform/per_workspace/output.json
ENVIRONMENT_MAPPING_YAML = $(CURDIR)/infrastructure/apigee/environment_mapping.yaml
STAGE_MAPPING_YAML = $(CURDIR)/infrastructure/apigee/stage_mapping.yaml

apigee--deploy: $(PROXYGEN_TIMESTAMP)

apigee--clean:
	[[ -f $(PROXYGEN_TIMESTAMP) ]] && rm $(PROXYGEN_TIMESTAMP) || :



$(PROXYGEN_TIMESTAMP): aws--login $(SWAGGER_APIGEE) $(WORKSPACE_OUTPUT_JSON) $(APIGEE_PEM)
	[[ -f $(PROXYGEN_TIMESTAMP) ]] && rm $(PROXYGEN_TIMESTAMP) || :

	WORKSPACE_OUTPUT_JSON=$(WORKSPACE_OUTPUT_JSON) \
	ENVIRONMENT_MAPPING_YAML=$(ENVIRONMENT_MAPPING_YAML) \
	STAGE_MAPPING_YAML=$(STAGE_MAPPING_YAML) \
	APIGEE_CONFIG_PATH=$(APIGEE_CONFIG_PATH) \
	SWAGGER_APIGEE=$(SWAGGER_APIGEE) \
		bash $(PATH_TO_INFRASTRUCTURE)/apigee/proxygen.sh generate_proxy

	touch $(PROXYGEN_TIMESTAMP)
