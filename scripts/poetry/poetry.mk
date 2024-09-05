.PHONY: poetry--update poetry--install poetry--clean

VENV_PYTHON = $(CURDIR)/.venv/bin/python
PYPROJECT_TOML = $(CURDIR)/pyproject.toml
POETRY_LOCK = $(CURDIR)/poetry.lock
TOOL_VERSIONS_COPY = $(TIMESTAMP_DIR)/tool-versions.copy

poetry--update: $(POETRY_LOCK) ## Updates installed dependencies as specified in pyproject.toml
poetry--install: $(VENV_PYTHON) ## First time installation of poetry configuration

poetry--clean:  ## Remove .venv directory
	[[ -d .venv ]] && rm -r .venv || :
	[[ -f $(POETRY_LOCK) ]] && rm $(POETRY_LOCK) || :

$(VENV_PYTHON):
	poetry -q || (pip install --upgrade pip && pip install poetry)
	[[ -f $(POETRY_LOCK) ]] && rm $(POETRY_LOCK) || :
	mkdir -p .venv
	poetry install --only main,dev --no-ansi
	.venv/bin/pre-commit install

$(POETRY_LOCK): $(TOOL_VERSIONS_COPY) $(VENV_PYTHON) $(PYPROJECT_TOML)
	poetry update --only main,dev
	touch $(POETRY_LOCK)
