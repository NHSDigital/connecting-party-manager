.PHONY: terraform--validate terraform--init terraform--plan terraform--apply terraform--destroy terraform--unlock initialise--mgmt destroy--mgmt initialise--non-mgmt automated-destroy destroy--non-mgmt corrupted--workspace-destroy corrupted--workspace-destroy

TERRAFORM_WORKSPACE =
ACCOUNT_WIDE = "non_account_wide"
TERRAFORM_ARGS =

PATH_TO_INFRASTRUCTURE := $(CURDIR)/scripts/infrastructure
PREFIX =
VERSION =

terraform--validate: _terraform--validate ## Run terraform validate
terraform--init: _terraform--init ## Run terraform init
terraform--plan: build terraform--init _terraform--plan  ## Run terraform plan
terraform--apply: _terraform--apply ## Run terraform apply
terraform--destroy: _terraform--destroy ## Run terraform destroy
terraform--unlock: _terraform--unlock ## Run terraform unlock
_terraform--%: aws--login
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh $* "$(TERRAFORM_WORKSPACE)" "$(ACCOUNT_WIDE)" "$(PARAMETER_DEPLOY)" "$(TERRAFORM_ARGS)"

initialise--mgmt: aws--login ## Bootstrap the MGMT AWS environment. Must provide PREFIX and VERSION keyword arguments.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/initialise-mgmt-resources.sh $(PREFIX) $(VERSION)

destroy--mgmt: aws--login ## Destroy the MGMT AWS environment. Must provide PREFIX and VERSION keyword arguments.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-mgmt-resources.sh $(PREFIX) $(VERSION)

initialise--non-mgmt: aws--login ## Bootstrap the Non-MGMT AWS environments. Must provide MGMT_ACCOUNT_ID and TERRAFORM_ROLE_NAME keyword arguments.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/initialise-non-mgmt-resources.sh $(MGMT_ACCOUNT_ID) $(TERRAFORM_ROLE_NAME)

destroy--non-mgmt: aws--login ## Destroy the Non-MGMT AWS environments. Must provide TERRAFORM_ROLE_NAME keyword argument.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-non-mgmt-resources.sh $(TERRAFORM_ROLE_NAME)

automated--destroy: aws--login ## Destroy any workspaces that have gone past their expiration date.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-expired-workspaces.sh

corrupted--workspace-destroy: aws--login ## Destroy any workspaces that cannot be detroyed with terraform.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-corrupted-workspace.sh $(TERRAFORM_WORKSPACE)
