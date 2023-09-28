.PHONY: poetry--update poetry--install poetry--clean

VENV_PYTHON = .venv/bin/python
VENV_TIMESTAMP = $(TIMESTAMP_DIR)/.venv.stamp

poetry--update: $(VENV_TIMESTAMP) ## Updates installed dependencies as specified in pyproject.toml

poetry--install: $(VENV_PYTHON) ## First time installation of poetry configuration

poetry--clean:  ## Remove .venv directory
	[[ -d .venv ]] && rm -r .venv || :

$(VENV_PYTHON): $(TOOL_TIMESTAMP)
	poetry -q || (pip install --upgrade pip && pip install poetry)
	mkdir -p .venv
	poetry install --with dev --no-ansi
	.venv/bin/pre-commit install
	touch $(VENV_PYTHON)

$(VENV_TIMESTAMP): $(TIMESTAMP_DIR) $(VENV_PYTHON) pyproject.toml
	poetry update
	touch $(VENV_TIMESTAMP)
