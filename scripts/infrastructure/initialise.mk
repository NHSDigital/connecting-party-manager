.PHONY: initialise--mgmt initialise--non-mgmt

initialise--mgmt: aws--login ## Bootstrap the MGMT AWS environment. Must provide PREFIX and VERSION keyword arguments.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/initialise-mgmt-resources.sh $(PREFIX) $(VERSION)

initialise--non-mgmt: aws--login ## Bootstrap the Non-MGMT AWS environments. Must provide MGMT_ACCOUNT_ID keyword arguments.
	@AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) bash $(PATH_TO_INFRASTRUCTURE)/initialise-non-mgmt-resources.sh $(MGMT_ACCOUNT_ID)
