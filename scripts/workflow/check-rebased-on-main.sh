#!/bin/bash

set -e

current_branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$current_branch" != "main" ]; then
  git fetch origin main:main
else
  git pull
fi

# Iterate over the commits in the current branch
for commit in $(git log ${current_branch}...origin/main --oneline --pretty=format:"%h"); do
    # Check if the commit is an ancestor of origin/main
    if git merge-base --is-ancestor origin/main $commit; then
        : # do nothing
    else
        echo "Current branch needs to be rebased on main"
        exit 1
    fi
done

echo "All commits are ancestors of origin/main"
