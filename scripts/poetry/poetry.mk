.PHONY: poetry--update poetry--install poetry--clean

VENV_PYTHON = .venv/bin/python
VENV_TIMESTAMP = .venv/.install.stamp

poetry--update: $(VENV_TIMESTAMP) ## Updates installed dependencies as specified in pyproject.toml

poetry--install: $(VENV_PYTHON) ## First time installation of poetry configuration

poetry--clean:  ## Remove .venv directory
	rm -r $(VENV_PYTHON)

$(VENV_PYTHON):
	poetry || (pip install --upgrade pip && pip install poetry)
	poetry config virtualenvs.in-project true
	poetry install --with dev --no-ansi
	.venv/bin/pre-commit install

$(VENV_TIMESTAMP): $(VENV_PYTHON) pyproject.toml
	poetry update
	touch $(VENV_TIMESTAMP)
