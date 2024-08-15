#!/bin/bash

# Run coverage of tests
coverage run -m pytest
coverage report --show-missing
coverage html
