.PHONY: terraform--plan terraform--apply terraform--destroy initialise--mgmt

PATH_TO_INFRASTRUCTURE := $(CURDIR)/scripts/infrastructure
PREFIX :=
VERSION :=
# UNCOMMENT THIS AFTER RUNNERS INSTALLED
# terraform--plan: build aws--login  ## Run terraform plan
#	@echo "terraform--plan" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION) $(TF_CLI_ARGS)

terraform--init: aws--login  ## Run terraform init
	@echo "terraform--init" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION) $(TF_CLI_ARGS)

# DELETE THIS AFTER RUNNERS INSTALLED
terraform--plan: terraform--init aws--login  ## Run terraform plan
	@echo "terraform--plan" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION) $(TF_CLI_ARGS)

terraform--apply: aws--login ## Run terraform apply
	@echo "terraform--apply" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION) $(TF_CLI_ARGS)

terraform--destroy: aws--login ## Run terraform destroy
	@echo "terraform--destroy" $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION) $(TF_CLI_ARGS)

initialise--mgmt: aws--login ## Bootstrap the MGMT AWS environment. Must provide PREFIX and VERSION keyword arguments.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/initialise-mgmt-resources.sh $(PREFIX) $(VERSION)

destroy--mgmt: aws--login ## Destroy the MGMT AWS environment. Must provide PREFIX and VERSION keyword arguments.
	@ AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-mgmt-resources.sh $(PREFIX) $(VERSION)
