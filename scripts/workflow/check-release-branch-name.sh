#!/bin/bash

# Get the current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Define a regular expression pattern to match the desired branch naming conventions
RELEASE_PATTERN="^release/[0-9]{4}-[0-9]{2}-[0-9]{2}(-[a-z])?$"

if [[ $CURRENT_BRANCH =~ $RELEASE_PATTERN ]]; then
    echo "The branch '$CURRENT_BRANCH' conforms to the release branch pattern."
    exit 0
else
    echo "The branch '$CURRENT_BRANCH' does not conform to the release branch pattern."
    exit 1
fi
