#!/bin/bash
set -e

# Get the current date in the format YYYY-MM-DD
CURRENT_DATE=$(date +"%Y-%m-%d")
RELEASE_PREFIX="release/"

# Check if the branch already exists
BRANCH_EXISTS=$(git rev-parse --verify "release/${CURRENT_DATE}" 2> /dev/null) || echo "ok"

# If the branch doesn't exist, create it with the current date
VERSION=${CURRENT_DATE}
if [ -z "${BRANCH_EXISTS}" ]; then
    BRANCH_NAME="${RELEASE_PREFIX}${CURRENT_DATE}"
else
    # If the branch exists, find an available sequential character
    for CHAR in {a..z}; do
        NEW_BRANCH_NAME="${RELEASE_PREFIX}${CURRENT_DATE}-${CHAR}"
        git rev-parse --verify "${NEW_BRANCH_NAME}" 2> /dev/null || break
    done
    VERSION=${CURRENT_DATE}-${CHAR}
    BRANCH_NAME="${NEW_BRANCH_NAME}"
fi

VERSION=${VERSION//-/.}

# Create the release branch
git checkout -b "$BRANCH_NAME"
poetry version ${VERSION}
echo ${VERSION} > VERSION
