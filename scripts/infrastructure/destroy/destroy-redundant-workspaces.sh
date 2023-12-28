#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-utils.sh

BRANCH_NAME="$1"
DESTROY_ALL_COMMITS_ON_BRANCH="$2"
KILL_ALL="$3"
CURRENT_COMMIT="$4"
AWS_REGION_NAME="eu-west-2"
ENV="dev"

function _get_valid_workspaces_to_destroy() {
    local object_name="$1"
    extract_commit=$"${object_name##*-}"
    if git rev-parse --quiet --verify "$extract_commit" > /dev/null 2>&1; then
        # Commit hasn't been squashed, Check if it's in the current branch.
        commits_in_branch=$(git log "$BRANCH_NAME"...origin/main --oneline --pretty=format:"%h")
        if echo "$commits_in_branch" | grep -q "$extract_commit"; then
            echo "$object_name"
        else
            if branches=$(git branch --contains "$commit_hash" 2>&1); then
                return
            else
                echo "$object_name"
            fi
        fi
    else
        # Commit was squashed
        echo "$object_name"
    fi
}

function _destroy_redundant_workspaces() {
    local bucket="s3://nhse-cpm--terraform-state-${VERSION}/${PROFILE_PREFIX}/"
    workspaces=$(aws s3 ls "$bucket" --no-paginate | awk '{print $NF}' | sed 's:/$::')

    # get JIRA ID from branch name
    if [[ $BRANCH_NAME =~ feature\/(PI-[0-9]+)[-_] ]]; then
        workspace_id="${BASH_REMATCH[1]}"
    elif [[ $BRANCH_NAME == *release/* ]]; then
        workspace_id="${BRANCH_NAME##*release/}"
    fi
    # get current short commit from branch
    if [ -z "$CURRENT_COMMIT" ]; then
        CURRENT_COMMIT=$(git rev-parse --short "$BRANCH_NAME")
    fi
    matching_objects=()

    # Loop through each line in the workspaces list
    while IFS= read -r object_name; do
        # Check if the object name contains the specified Jira ID
        if [[ -z "$DESTROY_ALL_COMMITS_ON_BRANCH" || "$DESTROY_ALL_COMMITS_ON_BRANCH" != "true" ]]; then
            if [[ $object_name == "ci-$workspace_id"* || $object_name == "rel-$workspace_id"* ]]; then
                if [[ ! $object_name == *"$CURRENT_COMMIT"* ]]; then
                    matching_object=$(_get_valid_workspaces_to_destroy "$object_name")
                    if [[ $matching_object ]]; then
                        matching_objects+=("$matching_object")
                    fi
                fi
            fi
        else
            # Destroy everything!
            if [[ $object_name == "ci-$workspace_id"* || $object_name == "rel-$workspace_id"* ]]; then
                if [[ -z "$KILL_ALL" || "$KILL_ALL" != "true" ]]; then
                    matching_object=$(_get_valid_workspaces_to_destroy "$object_name")
                    if [[ $matching_object ]]; then
                        matching_objects+=("$matching_object")
                    fi
                else
                    matching_objects+=("$object_name")
                fi
            fi
        fi
    done <<< "$workspaces"
    echo "$matching_objects"
    # Print the matching object names
    for workspace in "${matching_objects[@]}"; do
        echo "Attempting to destroy workspace: $workspace"
        bash ./scripts/infrastructure/terraform/terraform-commands.sh destroy $workspace "per_workspace" "" "-input=false -auto-approve -no-color"
    done
}

_destroy_redundant_workspaces
