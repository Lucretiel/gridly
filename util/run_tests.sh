#!/bin/sh

#Use a trap to preserve unittest's exit code
trap "coverage report -m" EXIT

coverage run --branch --source=gridly -m unittest test
