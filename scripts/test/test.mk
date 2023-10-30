.PHONY: _pytest _behave test--unit test--integration test--slow test--smoke test--feature--integration test--feature--local
_CACHE_CLEAR := "--cache-clear"

_pytest:
	poetry run python -m pytest $(PYTEST_FLAGS) $(_INTERNAL_FLAGS) $(_CACHE_CLEAR)

_behave:
	poetry run python -m behave feature-tests $(BEHAVE_FLAGS) $(_INTERNAL_FLAGS)

test--unit: ## Run unit (pytest) tests
	$(MAKE) _pytest _INTERNAL_FLAGS="-m 'unit' $(_INTERNAL_FLAGS)" _CACHE_CLEAR=$(_CACHE_CLEAR)

test--integration: aws--login ## Run integration (pytest) tests
	$(MAKE) _pytest _INTERNAL_FLAGS="-m 'integration' $(_INTERNAL_FLAGS)" _CACHE_CLEAR=$(_CACHE_CLEAR)

test--slow:  ## Run slow (pytest) tests
	$(MAKE) _pytest _INTERNAL_FLAGS="-m 'slow'" _CACHE_CLEAR=$(_CACHE_CLEAR)

test--smoke:  ## Run end-to-end smoke tests (pytest)
	$(MAKE) _pytest _INTERNAL_FLAGS="-m 'smoke'" _CACHE_CLEAR=$(_CACHE_CLEAR)

test--%--rerun: ## Rerun failed integration or unit (pytest) tests
	$(MAKE) test--$* _INTERNAL_FLAGS="--last-failed --last-failed-no-failures none" _CACHE_CLEAR=

test--feature--integration: aws--login ## Run integration feature (gherkin) tests
	$(MAKE) _behave _INTERNAL_FLAGS="--define='integration_test=true' $(_INTERNAL_FLAGS)"

test--feature--local: _behave  ## Run local feature (gherkin) tests

test--feature--%--auto-retry:  ## Autoretry of failed feature (gherkin) tests
	$(MAKE) test--feature--$* _INTERNAL_FLAGS="--define='auto_retry=true'"
