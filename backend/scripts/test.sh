#!/usr/bin/env bash

set -e
set -x

coverage run --source=app -m pytest "$@"
coverage report --show-missing --fail-under="${COVERAGE_FAIL_UNDER:-80}"
coverage html --title "${@-coverage}"
