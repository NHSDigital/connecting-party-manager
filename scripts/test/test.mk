.PHONY: _pytest _behave test--unit test--integration test--slow test--smoke test--feature--integration test--feature--local
_CACHE_CLEAR := "--cache-clear"

SDS_PROD_APIKEY =
SDS_DEV_APIKEY =
USE_CPM_PROD ?= FALSE
TEST_COUNT =
COMPARISON_ENV ?= local
RUN_SPEEDTEST = ?= FALSE
PROXYGEN_PRODUCT_TIMESTAMP = $(TIMESTAMP_DIR)/.proxygen-product.stamp

_pytest:
	AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) poetry run python -m pytest $(PYTEST_FLAGS) --ignore=archived_epr $(_INTERNAL_FLAGS) $(_CACHE_CLEAR)

_behave:
	AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) poetry run python -m behave src/api/tests/feature_tests $(BEHAVE_FLAGS) $(_INTERNAL_FLAGS) --no-skipped

test--unit: ## Run unit (pytest) tests
	$(MAKE) _pytest _INTERNAL_FLAGS="-m 'unit' $(_INTERNAL_FLAGS)" _CACHE_CLEAR=$(_CACHE_CLEAR)

test--integration: aws--login ## Run integration (pytest) tests
	$(MAKE) _pytest _INTERNAL_FLAGS="-m 'integration' $(_INTERNAL_FLAGS)" _CACHE_CLEAR=$(_CACHE_CLEAR) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN)

test--slow:  ## Run slow (pytest) tests
	$(MAKE) _pytest _INTERNAL_FLAGS="-m 'slow'" _CACHE_CLEAR=$(_CACHE_CLEAR)

# test--s3: aws--login ## Run (pytest) tests that require s3 downloads
# 	$(MAKE) _pytest _INTERNAL_FLAGS="-m 's3' $(_INTERNAL_FLAGS)" _CACHE_CLEAR=$(_CACHE_CLEAR) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN)

test--smoke: aws--login ## Run end-to-end smoke tests (pytest)
	AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) WORKSPACE=$(WORKSPACE) ACCOUNT=$(ACCOUNT) poetry run python -m pytest $(PYTEST_FLAGS) -m 'smoke' --ignore=src/layers --ignore=src/etl --ignore=archived_epr $(_CACHE_CLEAR)

test--%--rerun: ## Rerun failed integration or unit (pytest) tests
	$(MAKE) test--$* _INTERNAL_FLAGS="--last-failed --last-failed-no-failures none" _CACHE_CLEAR=$(_CACHE_CLEAR)

test--feature--integration: aws--login $(PROXYGEN_PRODUCT_TIMESTAMP) ## Run integration feature (gherkin) tests
	$(MAKE) _behave _INTERNAL_FLAGS="--define='test_mode=integration' --exclude='archived_epr/' $(_INTERNAL_FLAGS)" AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN)

test--feature--local: _behave  ## Run local feature (gherkin) tests

test--feature--%--auto-retry:  ## Autoretry of failed feature (gherkin) tests
	$(MAKE) test--feature--$* _INTERNAL_FLAGS="--define='auto_retry=true'"

test--coverage: aws--login ## Run unit (pytest) tests
		$(MAKE) _pytest _INTERNAL_FLAGS="--cov --cov-report=xml:sonarcloud-coverage.xml $(_INTERNAL_FLAGS)" _CACHE_CLEAR=$(_CACHE_CLEAR) AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN)
