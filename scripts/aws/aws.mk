.PHONY: aws--login

SSO_PROFILE ?= "mgmt-admin"
ROLE_NAME ?= "Admin"

AWS_CREDENTIALS :=
AWS_ACCESS_KEY_ID :=
AWS_SECRET_ACCESS_KEY :=
AWS_SESSION_TOKEN :=
AWS_SESSION_EXPIRY :=
AWS_DEFAULT_REGION = "eu-west-2"

ifeq ($(AWS_ACCESS_KEY_ID),)
aws--credentials:
	$(eval AWS_CREDENTIALS := $(shell ROLE_NAME=$(ROLE_NAME) PROFILE=$(PROJECT_PREFIX)$(SSO_PROFILE) bash scripts/aws/aws.sh))
	@VAR="$(AWS_CREDENTIALS)" bash scripts/aws/raise_if_empty.sh
	$(foreach stmt,$(AWS_CREDENTIALS),$(eval $(stmt)))
else
aws--credentials:
	echo "AWS_ACCESS_KEY_ID has been set, verifying if other environmental variables have been set"
	@VAR="$(AWS_ACCESS_KEY_ID)" bash scripts/aws/raise_if_empty.sh
	@VAR="$(AWS_SECRET_ACCESS_KEY)" bash scripts/aws/raise_if_empty.sh
	@VAR="$(AWS_SESSION_TOKEN)" bash scripts/aws/raise_if_empty.sh
endif

aws--login: aws--credentials ## Log in to AWS via SSO (account "mgmt" by default. Override by manually passing in AWS environmental variables)
