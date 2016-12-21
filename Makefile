PROJECT_ROOT ?= $(shell pwd)

LOCAL_SETTINGS = $(PROJECT_ROOT)/stepic_plugins/settings/local.py
DEFAULT_LOCAL_SETTINGS = $(PROJECT_ROOT)/contrib/dev_settings.py
REQUIREMENTS_DEV = $(PROJECT_ROOT)/requirements/dev.txt
VIRTUAL_ENV ?= $(shell pwd)
PIP = $(VIRTUAL_ENV)/bin/pip
PYTHON = $(VIRTUAL_ENV)/bin/python

SANDBOX_PYTHON_DIR := sandbox/python
SANDBOX_PIP = $(SANDBOX_PYTHON_DIR)/bin/pip
SANDBOX_REQUIREMENTS = $(PROJECT_ROOT)/requirements/sandbox_minimal.txt
VIRTUALENV_COMMAND ?= virtualenv --python `which python3`
ARENA_DIR = arena

.PHONY: init pip local-settings sandbox arena

init: pip local-settings sandbox

clean-local-settings:
	@[ -f "$(LOCAL_SETTINGS)" ] && rm -f $(LOCAL_SETTINGS) || true

pip:
	@$(PIP) install -U -r $(REQUIREMENTS_DEV)

local-settings:
	@[ ! -f "$(LOCAL_SETTINGS)" ] && cp $(DEFAULT_LOCAL_SETTINGS) $(LOCAL_SETTINGS) || true

sandbox: arena
	@mkdir -p $(SANDBOX_PYTHON_DIR)
	@[ ! -f "$(SANDBOX_PIP)" ] && $(VIRTUALENV_COMMAND) $(SANDBOX_PYTHON_DIR) || true
	@$(SANDBOX_PIP) install -U -r $(SANDBOX_REQUIREMENTS)

arena:
	@mkdir -p $(ARENA_DIR)

test-sandbox:
	@$(PYTHON) -m unittest -v $(PROJECT_ROOT)/sandbox_tests/tests.py

epicbox-init:
	@docker pull stepik/epicbox-base:alpine
	@docker pull stepik/epicbox-gcc:5.3.0
	@docker pull stepic/epicbox-python:latest
	@docker pull stepic/epicbox-trik:20151217
