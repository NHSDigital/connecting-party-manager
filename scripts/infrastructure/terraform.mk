.PHONY: terraform--validate terraform--init terraform--plan terraform--apply terraform--destroy terraform--unlock

AWS_ACCOUNT =
TERRAFORM_WORKSPACE =
TERRAFORM_SCOPE = "per_workspace"
TERRAFORM_ARGS =

PREFIX =
VERSION =

WORKSPACE_OUTPUT_JSON = $(CURDIR)/infrastructure/terraform/per_workspace/output.json
TERRAFORM_PLAN_TIMESTAMP = $(TIMESTAMP_DIR)/tfplan.timestamp
TERRAFORM_INIT_TIMESTAMP = $(TIMESTAMP_DIR)/tfinit.timestamp
BUILD_TIMESTAMP = $(TIMESTAMP_DIR)/.build.stamp

terraform--validate: _terraform--validate ## Run terraform validate
terraform--init: $(TERRAFORM_INIT_TIMESTAMP) ## Run terraform init
terraform--plan: $(TERRAFORM_PLAN_TIMESTAMP)  ## Run terraform plan
terraform--apply: $(WORKSPACE_OUTPUT_JSON) ## Run terraform apply
terraform--destroy: _terraform--destroy ## Run terraform destroy
terraform--unlock: _terraform--unlock ## Run terraform unlock
_terraform--%: aws--login
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh $* "${AWS_ACCOUNT}" "$(TERRAFORM_WORKSPACE)" "$(TERRAFORM_SCOPE)" "$(TERRAFORM_ARGS)"


$(TERRAFORM_INIT_TIMESTAMP): $(BUILD_TIMESTAMP)
	$(MAKE) _terraform--init
	touch $(TERRAFORM_INIT_TIMESTAMP)


$(TERRAFORM_PLAN_TIMESTAMP): $(TERRAFORM_INIT_TIMESTAMP)
	$(MAKE) _terraform--plan
	touch $(TERRAFORM_PLAN_TIMESTAMP)


$(WORKSPACE_OUTPUT_JSON): $(TERRAFORM_PLAN_TIMESTAMP)
	$(MAKE) _terraform--apply
