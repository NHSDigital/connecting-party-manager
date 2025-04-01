.PHONY: manage--non-mgmt-roles manage--non-mgmt-policies

manage--non-mgmt-roles: aws--login ## Create or update IAM Roles
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/roles/manage-non-mgmt-aws-roles.sh

manage--non-mgmt-policies: aws--login ## Create or update IAM Policies
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/roles/manage-non-mgmt-aws-deployment-policies.sh

manage--non-mgmt-development-policies: aws--login ## Create or update IAM Policies
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/roles/manage-non-mgmt-aws-development-policies.sh

manage--mgmt-development-policies: aws--login ## Create or update IAM Policies
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/roles/manage-mgmt-aws-development-policies.sh

manage--non-mgmt-support-policies: aws--login ## Create or update IAM Policies
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/roles/manage-non-mgmt-aws-support-policies.sh

manage--mgmt-support-policies: aws--login ## Create or update IAM Policies
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/roles/manage-mgmt-aws-support-policies.sh

manage--non-mgmt-test-policies: aws--login ## Create or update IAM Policies
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/roles/manage-non-mgmt-aws-support-integration-policies.sh

manage--non-mgmt-trust-policies: aws--login ## Create or update IAM Policies
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/roles/manage-non-mgmt-aws-trust-policy.sh
