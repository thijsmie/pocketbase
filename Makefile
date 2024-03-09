#!/usr/bin/make -f

.DEFAULT_GOAL := help

.ONESHELL:

# ENV VARS
export SHELL := $(shell which sh)
export UNAME := $(shell uname -s)
export ASDF_VERSION := v0.13.1

# check commands and OS
ifeq ($(UNAME), Darwin)
	export XCODE := $(shell xcode-select -p 2>/dev/null)
	export HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK := 1
else ifeq ($(UNAME), Linux)
    include /etc/os-release
endif

export ASDF := $(shell command -v asdf 2>/dev/null)
export BREW := $(shell command -v brew 2>/dev/null)
export DEVBOX := $(shell command -v devbox 2>/dev/null)
export GIT := $(shell command -v git 2>/dev/null)
export PRE_COMMIT := $(shell command -v pre-commit 2>/dev/null)
export TASK := $(shell command -v task 2>/dev/null)

# colors
GREEN := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE := $(shell tput -Txterm setaf 7)
CYAN := $(shell tput -Txterm setaf 6)
RESET := $(shell tput -Txterm sgr0)

# targets
.PHONY: all
all: help asdf xcode brew devbox pre-commit task ## run all targets

xcode: ## install xcode command line tools
ifeq ($(UNAME), Darwin)
	@if [ -z "${XCODE}" ]; then \
		echo "Installing Xcode command line tools..."; \
		xcode-select --install; \
	else \
		echo "xcode already installed."; \
	fi
else
	@echo "xcode not supported."
endif

brew: xcode ## install homebrew
ifeq ($(UNAME), Darwin)
	@if [ -z "${BREW}" ]; then \
		echo "Installing Homebrew..."; \
		/bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; \
	else \
		echo "brew already installed."; \
	fi
else
	@echo "brew not supported."
endif

devbox: ## install devbox
	@if [ -z "${DEVBOX}" ]; then \
		echo "Installing devbox..."; \
		curl -fsSL https://get.jetpack.io/devbox | bash; \
	else \
		echo "devbox already installed."; \
	fi

asdf: xcode ## install asdf
ifeq ($(UNAME), Darwin)
	@if [ -z "${ASDF}" ]; then \
		echo "Installing asdf..."; \
		git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch ${ASDF_VERSION}; \
		echo "To use asdf, add the following to your shell rc (.bashrc/.zshrc):"; \
		echo "export PATH=\"$$HOME/.asdf/shims:$$PATH\""; \
		echo ". $$HOME/.asdf/asdf.sh"; \
		echo ". $$HOME/.asdf/completions/asdf.bash"; \
	else \
		echo "asdf already installed."; \
	fi
endif

git: ## install git
	@if [ -n "${GIT}" ]; then \
		echo "git already installed."; \
		exit 0; \
	fi
	if [ "${UNAME}" = "Darwin" ] && [ -n "${BREW}" ]; then \
		brew install git; \
	elif [ "${ID}" = "ubuntu" ] || [ "${ID_LIKE}" = "debian" ]; then \
		sudo apt install -y git; \
	else \
		echo "Uncaught error"; \
	fi

pre-commit: ## install pre-commit
	@if [ -n "${PRE_COMMIT}" ]; then \
		echo "pre-commit already installed."; \
		exit 0; \
	fi
	@if [ "${UNAME}" = "Darwin" ] && [ -n "${BREW}" ]; then \
		brew install pre-commit; \
	elif [ "${ID}" = "ubuntu" ] || [ "${ID_LIKE}" = "debian" ]; then \
		python3 -m pip install pre-commit; \
	else \
		echo "Uncaught error"; \
	fi

task: ## install taskfile
ifeq ($(UNAME), Darwin)
	@if [ -z "${TASK}" ] && [ ! -z "${BREW}" ]; then \
		echo "Installing taskfile..."; \
		brew install go-task; \
	else \
		echo "taskfile already installed."; \
	fi
else ifeq ($(UNAME), Linux)
	@if [ -z "${TASK}" ] && [ "${ID_LIKE}" = "debian" ]; then \
		echo "Installing taskfile..."; \
		sudo snap install task --classic; \
	else \
		echo "taskfile already installed."; \
	fi
else
	@echo "taskfile not supported."
endif

install: xcode asdf brew devbox pre-commit task ## install dependencies

help: ## show this help
	@echo ''
	@echo 'Usage:'
	@echo '    ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} { \
		if (/^[a-zA-Z_-]+:.*?##.*$$/) {printf "    ${YELLOW}%-20s${GREEN}%s${RESET}\n", $$1, $$2} \
		else if (/^## .*$$/) {printf "  ${CYAN}%s${RESET}\n", substr($$1,4)} \
		}' $(MAKEFILE_LIST)
