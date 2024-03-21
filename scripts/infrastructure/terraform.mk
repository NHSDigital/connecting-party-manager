.PHONY: terraform--validate terraform--init terraform--plan terraform--apply terraform--destroy terraform--unlock

AWS_ACCOUNT =
TERRAFORM_WORKSPACE =
TERRAFORM_SCOPE = "per_workspace"
TERRAFORM_ARGS =

PREFIX =
VERSION =

WORKSPACE_OUTPUT_JSON = $(CURDIR)/infrastructure/terraform/per_workspace/output.json
TERRAFORM_PLAN_TIMESTAMP = $(TIMESTAMP_DIR)/tfplan.timestamp
BUILD_TIMESTAMP = $(TIMESTAMP_DIR)/.build.timestamp
TERRAFORM_FILES = $(shell find infrastructure/terraform -type f -name "*.tf*") $(shell find infrastructure/terraform -type f -name "*.asl.json")

terraform--clean:
	[[ -f $(TERRAFORM_PLAN_TIMESTAMP) ]] && rm $(TERRAFORM_PLAN_TIMESTAMP) || :
	[[ -f $(WORKSPACE_OUTPUT_JSON) ]] && rm $(WORKSPACE_OUTPUT_JSON) || :
terraform--validate: _terraform--validate ## Run terraform validate
terraform--init: _terraform--init ## Run terraform init
terraform--plan: $(TERRAFORM_PLAN_TIMESTAMP)  ## Run terraform plan
terraform--apply: $(WORKSPACE_OUTPUT_JSON) ## Run terraform apply
terraform--apply--force: terraform--clean terraform--apply ## Run terraform apply

terraform--destroy: _terraform--destroy ## Run terraform destroy
terraform--unlock: _terraform--unlock ## Run terraform unlock
_terraform--%: aws--login
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh $* "${AWS_ACCOUNT}" "$(TERRAFORM_WORKSPACE)" "$(TERRAFORM_SCOPE)" "$(TERRAFORM_ARGS)"

$(TERRAFORM_PLAN_TIMESTAMP): $(BUILD_TIMESTAMP) $(TERRAFORM_FILES)
	$(MAKE) _terraform--plan
	touch $(TERRAFORM_PLAN_TIMESTAMP)


$(WORKSPACE_OUTPUT_JSON): $(TERRAFORM_PLAN_TIMESTAMP)
	$(MAKE) _terraform--apply
