#!/bin/bash

set -e

MAIN="main"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "${MAIN}" ]; then
  git fetch origin ${MAIN}:${MAIN}
else
  git pull
fi

# Iterate over the commits in the current branch
for COMMIT in $(git log ${CURRENT_BRANCH}...origin/${MAIN} --oneline --pretty=format:"%h"); do
    # Check if the commit is an ancestor of origin/main
    echo "-- commit: ${COMMIT}"
    if git merge-base --is-ancestor origin/${MAIN} ${COMMIT}; then
        : # do nothing
    else
        echo "Current branch needs to be rebased on ${MAIN}"
        exit 1
    fi
done

echo "All commits are ancestors of origin/${MAIN}"
