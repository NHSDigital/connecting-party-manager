.PHONY: destroy--mgmt destroy--non-mgmt destroy--expired destroy--corrupted

destroy--mgmt: aws--login ## Destroy the MGMT AWS environment. Must provide PREFIX and VERSION keyword arguments.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-mgmt-resources.sh $(PREFIX) $(VERSION)

destroy--non-mgmt: aws--login ## Destroy the Non-MGMT AWS environments. Must provide TERRAFORM_ROLE_NAME keyword argument.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-non-mgmt-resources.sh

destroy--expired: aws--login ## Destroy any workspaces that have gone past their expiration date.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-expired-workspaces.sh

destroy--corrupted: aws--login ## Destroy any workspaces that cannot be detroyed with terraform.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/destroy-corrupted-workspace.sh $(TERRAFORM_WORKSPACE)
