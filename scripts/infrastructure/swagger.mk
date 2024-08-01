.PHONY: swagger--merge swagger--clean

WORKSPACE_OUTPUT_JSON = $(CURDIR)/infrastructure/terraform/per_workspace/output.json
VENV_PYTHON = $(CURDIR)/.venv/bin/python
INIT_TIMESTAMP = $(CURDIR)/.timestamp/init.timestamp

SWAGGER_DIST = $(CURDIR)/infrastructure/swagger/dist
SWAGGER_AWS = $(SWAGGER_DIST)/aws/swagger.yaml
SWAGGER_PUBLIC = $(SWAGGER_DIST)/public/swagger.yaml
SWAGGER_APIGEE = $(SWAGGER_DIST)/apigee/swagger.yaml
_CLEANED_SWAGGER_FILE = $(SWAGGER_DIST)/build/_02_clean.yaml

TOOL_VERSIONS_COPY = $(TIMESTAMP_DIR)/tool-versions.copy
SWAGGER_DEPENDENCIES = $(shell find infrastructure/swagger -type f -name "*.yaml" -not -path "*/dist/*.yaml" ) $(shell find scripts/infrastructure/swagger -type f -name "*.sh") $(TOOL_VERSIONS_COPY)

swagger--merge--aws: $(SWAGGER_AWS) ## Updates API Gateway swagger builds from the components in the infrastructure/swagger/ directory.
swagger--merge--public: $(SWAGGER_PUBLIC) ## Updates public swagger builds from the components in the infrastructure/swagger/ directory.
swagger--merge--apigee: $(SWAGGER_APIGEE) ## Updates Apigee swagger builds from the components in the infrastructure/swagger/ directory.
swagger--clean:  ## Removes swagger builds.
	[[ -d $(SWAGGER_DIST) ]] && rm -r $(SWAGGER_DIST) || :


$(_CLEANED_SWAGGER_FILE): $(SWAGGER_DEPENDENCIES)
	@env bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh merge_base

$(SWAGGER_AWS): $(SWAGGER_DEPENDENCIES) $(_CLEANED_SWAGGER_FILE)
	@env bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh generate_aws_swagger
	npx --yes @redocly/cli lint $(SWAGGER_AWS) --skip-rule operation-4xx-response --skip-rule spec-components-invalid-map-name

$(SWAGGER_PUBLIC): $(SWAGGER_DEPENDENCIES) $(_CLEANED_SWAGGER_FILE)
	@env bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh generate_public_swagger
	npx --yes @redocly/cli lint $(SWAGGER_PUBLIC) --skip-rule security-defined

$(SWAGGER_APIGEE): $(SWAGGER_DEPENDENCIES) $(_CLEANED_SWAGGER_FILE) $(WORKSPACE_OUTPUT_JSON)
	@env bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh generate_apigee_swagger
	npx --yes @redocly/cli lint $(SWAGGER_APIGEE) --skip-rule security-defined
