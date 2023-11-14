#!/bin/bash

branch=$(git symbolic-ref --short HEAD)
if [[ "${branch}" == *"release/"* ]]; then
    result=`python ./scripts/changelog/changelog_precommit.py $branch`
    if [[ "${result}" == "updated" ]]; then
        echo "SUCCESS: CHANGELOG.md has now been updated: please re-commit."
        exit 1
    elif [[ "${result}" == "file_not_found" ]]; then
        echo "FAILURE: File not found- changelog/${branch}.md"
        exit 1
    elif [[ "${result}" == "nothing_to_do" ]]; then
        exit 0
    else
        echo ${result}
        exit 1
    fi
else
    echo "Not a release branch, skipping"
    exit 0
fi
