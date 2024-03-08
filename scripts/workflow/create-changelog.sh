#!/bin/bash

# Get the current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Extract the version from the name
VERSION=${CURRENT_BRANCH#*/}

touch changelog/${VERSION}.md
