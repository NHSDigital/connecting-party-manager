etl--clear-state: aws--login ## Clear the ETL state
	AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) poetry run python scripts/etl/clear_state_inputs.py
