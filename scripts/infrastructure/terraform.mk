.PHONY: terraform--plan terraform--apply terraform--destroy initialise--mgmt

TERRAFORM_COMMAND ?= "validate"
TERRAFORM_ENVIRONMENT ?= "dev"
TERRAFORM_ACCOUNT_WIDE ?= "non_account_wide"
TERRAFORM_ARGS :=

PATH_TO_INFRASTRUCTURE := $(CURDIR)/scripts/infrastructure
PREFIX :=
VERSION :=
# UNCOMMENT THIS AFTER RUNNERS INSTALLED
# terraform--plan: build aws--login  ## Run terraform plan
#	@echo "terraform--plan" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION) $(TF_CLI_ARGS)

terraform--validate: ## Run terraform validate
	@bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh $(TERRAFORM_COMMAND) $(TERRAFORM_ENVIRONMENT) $(TERRAFORM_ACCOUNT_WIDE) $(TERRAFORM_ARGS)

# terraform--%: aws--login ## Run terraform commands
# 	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh $* $(TERRAFORM_ENVIRONMENT) $(TERRAFORM_ACCOUNT_WIDE) $(TERRAFORM_ARGS)

terraform--init: aws--login ## Run terraform init
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh init $(TERRAFORM_ENVIRONMENT) $(TERRAFORM_ACCOUNT_WIDE) $(TERRAFORM_ARGS)

# DELETE THIS AFTER RUNNERS INSTALLED
terraform--plan: aws--login  ## Run terraform plan
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh plan $(TERRAFORM_ENVIRONMENT) $(TERRAFORM_ACCOUNT_WIDE) $(TERRAFORM_ARGS)

terraform--apply: terraform--plan ## Run terraform apply
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh apply $(TERRAFORM_ENVIRONMENT) $(TERRAFORM_ACCOUNT_WIDE) $(TERRAFORM_ARGS)

terraform--destroy: aws--login ## Run terraform destroy
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh destroy $(TERRAFORM_ENVIRONMENT) $(TERRAFORM_ACCOUNT_WIDE) $(TERRAFORM_ARGS)

initialise--mgmt: aws--login ## Bootstrap the MGMT AWS environment. Must provide PREFIX and VERSION keyword arguments.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/initialise-mgmt-resources.sh $(PREFIX) $(VERSION)

destroy--mgmt: aws--login ## Destroy the MGMT AWS environment. Must provide PREFIX and VERSION keyword arguments.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-mgmt-resources.sh $(PREFIX) $(VERSION)

initialise--non-mgmt: aws--login ## Bootstrap the Non-MGMT AWS environments. Must provide MGMT_ACCOUNT_ID and TERRAFORM_ROLE_NAME keyword arguments.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/initialise-non-mgmt-resources.sh $(MGMT_ACCOUNT_ID) $(TERRAFORM_ROLE_NAME)

destroy--non-mgmt: aws--login ## Destroy the Non-MGMT AWS environments. Must provide TERRAFORM_ROLE_NAME keyword argument.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-non-mgmt-resources.sh $(TERRAFORM_ROLE_NAME)
