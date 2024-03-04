#!/bin/bash

# Get the current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

git commit -m "[${CURRENT_BRANCH}] Create release"
