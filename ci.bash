#!/bin/bash

set -eux -o pipefail

ruff format src tests examples
ruff check --fix src tests
mypy src
pytest --cov=pocketbase
coverage report -m --skip-covered --skip-empty
