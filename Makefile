LOCAL_SETTINGS = stepic_plugins/local_settings.py
DEFAULT_LOCAL_SETTINGS = contrib/dev_settings.py
REQUIREMENTS_DEV = requirements/dev.txt
VIRTUAL_ENV ?= .
PIP = $(VIRTUAL_ENV)/bin/pip

SANDBOX_PYTHON_DIR := sandbox/python
SANDBOX_PIP = $(SANDBOX_PYTHON_DIR)/bin/pip
SANDBOX_REQUIREMENTS = requirements/sandbox_minimal.txt
VIRTUALENV_COMMAND := virtualenv --python `which python3`
ARENA_DIR = arena

.PHONY: init pip local-settings sandbox arena

init: pip local-settings sandbox arena

pip:
	@$(PIP) install -r $(REQUIREMENTS_DEV)

local-settings:
	@[ ! -f "$(LOCAL_SETTINGS)" ] && cp $(DEFAULT_LOCAL_SETTINGS) $(LOCAL_SETTINGS) || true

sandbox:
	@mkdir -p $(SANDBOX_PYTHON_DIR)
	@$(VIRTUALENV_COMMAND) $(SANDBOX_PYTHON_DIR)
	@$(SANDBOX_PIP) install -r $(SANDBOX_REQUIREMENTS)

arena:
	@mkdir -p $(ARENA_DIR)
