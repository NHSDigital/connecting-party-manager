#!/bin/bash

# Get the current branch name
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Define a regular expression pattern to match the desired branch naming conventions
feature_pattern="^feature/PI-[0-9]+-[A-Za-z]*$"
release_pattern="^release/[0-9]{4}-[0-9]{2}-[0-9]{2}(-[a-z])?$"

if [[ $current_branch =~ $feature_pattern ]]; then
    echo "The branch '$current_branch' conforms to the feature branch pattern."
    exit 0
elif [[ $current_branch =~ $release_pattern ]]; then
    echo "The branch '$current_branch' conforms to the release branch pattern."
    exit 0
else
    echo "The branch '$current_branch' does not conform to any of the allowed patterns."
    exit 1
fi
