.PHONY: swagger--merge

SWAGGER_TIMESTAMP = $(TIMESTAMP_DIR)/.swagger.stamp
SWAGGER_DIST = $(CURDIR)/infrastructure/swagger/dist
SWAGGER_AWS = $(SWAGGER_DIST)/aws/swagger.yaml
SWAGGER_PUBLIC = $(SWAGGER_DIST)/public/swagger.yaml

swagger--merge: $(SWAGGER_AWS) $(SWAGGER_PUBLIC) ## Updates swagger builds from the components in the infrastructure/swagger/ directory.
swagger--clean:  ## Removes swagger builds.
	[[ -f $(SWAGGER_TIMESTAMP) ]] && rm $(SWAGGER_TIMESTAMP) || :
	[[ -d $(SWAGGER_DIST) ]] && rm -r $(SWAGGER_DIST) || :


$(SWAGGER_TIMESTAMP): $(TIMESTAMP_DIR)
	touch $(SWAGGER_TIMESTAMP)

$(CURDIR)/infrastructure/swagger/dist/%/swagger.yaml: $(SWAGGER_TIMESTAMP) $(shell find infrastructure/swagger -type f -name "*.yaml" -not -path "*/dist/*.yaml" )
	@bash $(PATH_TO_INFRASTRUCTURE)/swagger/merge.sh
	poetry run pytest infrastructure/swagger || ([[ -f $(SWAGGER_TIMESTAMP) ]] && rm $(SWAGGER_TIMESTAMP) || :; exit 1)
