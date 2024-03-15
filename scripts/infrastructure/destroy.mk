.PHONY: destroy--mgmt destroy--non-mgmt destroy--expired destroy--corrupted destroy--redundant-workspaces

destroy--mgmt: aws--login ## Destroy the MGMT AWS environment. Must provide PREFIX and VERSION keyword arguments.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	bash $(PATH_TO_INFRASTRUCTURE)/destroy/destroy-mgmt-resources.sh $(PREFIX) $(VERSION)

destroy--non-mgmt: aws--login ## Destroy the Non-MGMT AWS environments. Must provide TERRAFORM_ROLE_NAME keyword argument.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	bash $(PATH_TO_INFRASTRUCTURE)/destroy/destroy-non-mgmt-resources.sh

destroy--expired: aws--login ## Destroy any workspaces that have gone past their expiration date.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	bash $(PATH_TO_INFRASTRUCTURE)/destroy/destroy-expired-workspaces.sh $(ENVIRONMENT)

destroy--corrupted: aws--login ## Destroy any workspaces that cannot be detroyed with terraform.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	bash $(PATH_TO_INFRASTRUCTURE)/destroy/destroy-corrupted-workspace.sh $(TERRAFORM_WORKSPACE)

destroy--redundant-workspaces: aws--login ## Destroy any workspaces that are associated with a branch when they are not the latest commit.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	bash $(PATH_TO_INFRASTRUCTURE)/destroy/destroy-redundant-workspaces.sh $(BRANCH_NAME) $(DESTROY_ALL_COMMITS_ON_BRANCH) $(KILL_ALL) $(CURRENT_COMMIT)
