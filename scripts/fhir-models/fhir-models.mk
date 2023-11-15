.PHONY: fhir--models fhir--models--clean _datamodel-codegen

FHIR_MODELS_SCRIPTS_DIR = $(CURDIR)/scripts/fhir-models
FHIR_MODEL_PATH = $(CURDIR)/src/layers/domain/fhir/r4
NORMAL_MODEL_PATH := $(FHIR_MODEL_PATH)/models.py
STRICT_MODEL_PATH := $(FHIR_MODEL_PATH)/strict_models.py

fhir--models: $(NORMAL_MODEL_PATH) $(STRICT_MODEL_PATH)
fhir--models--clean:
	[[ -f $(NORMAL_MODEL_PATH) ]] && rm $(NORMAL_MODEL_PATH) || :
	[[ -f $(STRICT_MODEL_PATH) ]] && rm $(STRICT_MODEL_PATH) || :


$(NORMAL_MODEL_PATH): $(shell find infrastructure/swagger -type f -name "*.yaml" -not -path "*/dist/*.yaml" )
	$(MAKE) swagger--merge
	@MODEL_PATH=$(NORMAL_MODEL_PATH) SWAGGER_AWS=$(SWAGGER_AWS) bash $(FHIR_MODELS_SCRIPTS_DIR)/datamodel-codegen.sh


$(STRICT_MODEL_PATH): $(shell find infrastructure/swagger -type f -name "*.yaml" -not -path "*/dist/*.yaml" )
	$(MAKE) swagger--merge
	@MODEL_PATH=$(STRICT_MODEL_PATH) SWAGGER_AWS=$(SWAGGER_AWS) EXTRA_CODEGEN_ARGS="--strict-types str --strict-types bytes --strict-types int --strict-types float --strict-types bool" bash $(FHIR_MODELS_SCRIPTS_DIR)/datamodel-codegen.sh
