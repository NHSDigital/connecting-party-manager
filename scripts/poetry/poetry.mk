.PHONY: poetry--update poetry--install poetry--clean

VENV_PYTHON = $(CURDIR)/.venv/bin/python
PYPROJECT_TOML = $(CURDIR)/pyproject.toml
POETRY_LOCK = $(CURDIR)/poetry.lock

poetry--update: $(POETRY_LOCK) ## Updates installed dependencies as specified in pyproject.toml
poetry--install: $(VENV_PYTHON) ## First time installation of poetry configuration

poetry--clean:  ## Remove .venv directory
	[[ -d .venv ]] && rm -r .venv || :
	[[ -f $(POETRY_LOCK) ]] && rm $(POETRY_LOCK) || :

$(VENV_PYTHON):
	poetry -q || (pip install --upgrade pip && pip install poetry)
	mkdir -p .venv
	poetry install --with dev --no-ansi
	.venv/bin/pre-commit install
	touch $(VENV_PYTHON)

$(POETRY_LOCK): $(TIMESTAMP_DIR) $(VENV_PYTHON) $(PYPROJECT_TOML)
	poetry update
	touch $(POETRY_LOCK)
