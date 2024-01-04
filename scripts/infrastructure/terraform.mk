.PHONY: terraform--validate terraform--init terraform--plan terraform--apply terraform--destroy terraform--unlock

AWS_ACCOUNT =
TERRAFORM_WORKSPACE =
TERRAFORM_SCOPE = "per_workspace"
TERRAFORM_ARGS =

PREFIX =
VERSION =

terraform--validate: _terraform--validate ## Run terraform validate
terraform--init: _terraform--init ## Run terraform init
terraform--plan: build terraform--init _terraform--plan  ## Run terraform plan
terraform--apply: _terraform--apply ## Run terraform apply
terraform--destroy: _terraform--destroy ## Run terraform destroy
terraform--unlock: _terraform--unlock ## Run terraform unlock
_terraform--%: aws--login
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	bash $(PATH_TO_INFRASTRUCTURE)/terraform/terraform-commands.sh $* "${AWS_ACCOUNT}" "$(TERRAFORM_WORKSPACE)" "$(TERRAFORM_SCOPE)" "$(TERRAFORM_ARGS)"
