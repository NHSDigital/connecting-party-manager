SET_CHANGELOG_NUMBER :=
WORKSPACE :=

etl--clear-state: aws--login ## Clear the ETL state
	AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) poetry run python scripts/etl/clear_state_inputs.py "$(SET_CHANGELOG_NUMBER)" "$(WORKSPACE)"


etl--head-state--developer: aws--login ## Download the head of the ETL state
	AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) poetry run python scripts/etl/head_etl.py ""

etl--head-state--persistent-workspace: ## Download the head of the ETL state (for persistent workspaces)
	@if [ -z "$(WORKSPACE)" ]; then \
		echo "Error: WORKSPACE must be provided."; \
		exit 1; \
	fi

	$(eval AWS_ACCESS_KEY_ID = $(shell echo $${AWS_ACCESS_KEY_ID}))
	$(eval AWS_SECRET_ACCESS_KEY = $(shell echo $${AWS_SECRET_ACCESS_KEY}))
	$(eval AWS_SESSION_TOKEN = $(shell echo $${AWS_SESSION_TOKEN}))

	@if [ -z "$(AWS_DEFAULT_REGION)" ] || [ -z "$(AWS_ACCESS_KEY_ID)" ] || [ -z "$(AWS_SECRET_ACCESS_KEY)" ] || [ -z "$(AWS_SESSION_TOKEN)" ]; then \
		echo "Error: You must have logged into ${WORKSPACE} first. For example, you can copy and paste the credentials from the SSO GUI into the terminal."; \
		exit 1; \
	fi
	AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) poetry run python scripts/etl/head_etl.py "$(WORKSPACE)"
