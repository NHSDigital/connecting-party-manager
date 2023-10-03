.PHONY: aws--login

aws--login:  ## Log in to AWS via SSO (account "mgmt" by default)
	@echo "aws--login"  $(CI) $(WORKSPACE) $(AWS_ACCESS_KEY_ID) $(AWS_SECRET_ACCESS_KEY) $(AWS_DEFAULT_REGION)
	# @aws sts get-caller-identity --profile $(PROFILE) || aws sso login --profile $(SSO_PROFILE)
	# @AWS_CREDENTIALS=$$(aws sts assume-role --profile $(PROFILE)\
	# 	| jq -r '.Credentials\
	# 	| "export AWS_ACCESS_KEY_ID=\(.AccessKeyId) AWS_SECRET_ACCESS_KEY=\(.SecretAccessKey) AWS_SESSION_TOKEN=\(.SessionToken)"')
	# @eval $${AWS_CREDENTIALS}
