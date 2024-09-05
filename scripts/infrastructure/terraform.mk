.PHONY: terraform--validate terraform--init terraform--plan terraform--apply terraform--destroy terraform--unlock

AWS_ACCOUNT =
TERRAFORM_WORKSPACE =
TERRAFORM_SCOPE = per_workspace
TERRAFORM_ARGS =

PREFIX =
VERSION =

WORKSPACE_OUTPUT_JSON = $(CURDIR)/infrastructure/terraform/per_workspace/output.json
TERRAFORM_PLAN_TIMESTAMP = $(TIMESTAMP_DIR)/tfplan.timestamp
BUILD_TIMESTAMP = $(TIMESTAMP_DIR)/.build.timestamp
TERRAFORM_FILES = $(shell find infrastructure/terraform/per_workspace -type f -name "*.tf*") $(shell find infrastructure/terraform -type f -name "*.asl.json")

terraform--clean:
	[[ -f $(TERRAFORM_PLAN_TIMESTAMP) ]] && rm $(TERRAFORM_PLAN_TIMESTAMP) || :
	[[ -f $(WORKSPACE_OUTPUT_JSON) ]] && rm $(WORKSPACE_OUTPUT_JSON) || :
	$(MAKE) _terraform--clean
terraform--validate: _terraform--validate ## Run terraform validate
terraform--init: _terraform--init ## Run terraform init
terraform--plan: $(TERRAFORM_PLAN_TIMESTAMP)--$(TERRAFORM_SCOPE)  ## Run terraform plan
terraform--apply: $(WORKSPACE_OUTPUT_JSON) ## Run terraform apply
terraform--apply--force: terraform--clean terraform--apply ## Run terraform apply
terraform--destroy: _terraform--destroy ## Run terraform destroy

terraform--init--upgrade:
	$(MAKE) terraform--init TERRAFORM_ARGS=-upgrade

terraform--plan--qa: ## Run terraform plan against qa
	$(MAKE) terraform--plan AWS_ACCOUNT=qa
terraform--apply--qa: ## Run terraform apply against qa
	$(MAKE) terraform--apply AWS_ACCOUNT=qa
terraform--destroy--qa: ## Run terraform destroy on qa workspace
	$(MAKE) terraform--destroy AWS_ACCOUNT=qa

terraform--unlock: _terraform--unlock ## Run terraform unlock
_terraform--%: aws--login
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh $* "${AWS_ACCOUNT}" "$(TERRAFORM_WORKSPACE)" "$(TERRAFORM_SCOPE)" "$(TERRAFORM_ARGS)"

$(TERRAFORM_PLAN_TIMESTAMP)--per_workspace: $(BUILD_TIMESTAMP) $(TERRAFORM_FILES)
	$(MAKE) _terraform--plan
	touch $(TERRAFORM_PLAN_TIMESTAMP)--per_workspace

$(TERRAFORM_PLAN_TIMESTAMP)--%: $(TOOL_VERSIONS_COPY)
	$(MAKE) _terraform--plan
	bash $(PATH_TO_INFRASTRUCTURE)/terraform/touch.sh $(TERRAFORM_PLAN_TIMESTAMP)--$*

$(WORKSPACE_OUTPUT_JSON): $(TERRAFORM_PLAN_TIMESTAMP)--$(TERRAFORM_SCOPE)
	$(MAKE) _terraform--apply
