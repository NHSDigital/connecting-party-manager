#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-utils.sh

AWS_REGION_NAME="eu-west-2"
ENV="dev"

function _destroy_expired_workspaces() {
    dev_acct=$(_get_aws_account_id "$ENV" "$PROFILE_PREFIX" "$VERSION")
    role_arn="arn:aws:iam::${dev_acct}:role/NHSDeploymentRole"
    session_name="resource-search-session"
    duration_seconds=900
    assume_role_output=$(aws sts assume-role --role-arn "$role_arn" --role-session-name "$session_name" --duration-seconds "$duration_seconds")

    # Check if the assume-role command was successful
    if [ $? -eq 0 ]; then
        MGMT_AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
        MGMT_AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
        MGMT_AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
        # Extract temporary credentials from the assume-role output
        access_key=$(echo "$assume_role_output" | jq -r '.Credentials.AccessKeyId')
        secret_key=$(echo "$assume_role_output" | jq -r '.Credentials.SecretAccessKey')
        session_token=$(echo "$assume_role_output" | jq -r '.Credentials.SessionToken')

        # Export temporary credentials as environment variables
        export AWS_ACCESS_KEY_ID="$access_key"
        export AWS_SECRET_ACCESS_KEY="$secret_key"
        export AWS_SESSION_TOKEN="$session_token"

        workspaces=()
        pwd #remove
        groups=$(aws resource-groups search-resources --resource-query file://scripts/infrastructure/destroy/expired-workspace-query.json --region "${AWS_REGION_NAME}")
        if [ $? -eq 0 ]; then
            resourceArns=($(echo "$groups" | jq -r '.ResourceIdentifiers[].ResourceArn'))
            for arn in "${resourceArns[@]}"; do
                tagsResult=$(aws resource-groups get-tags --arn "$arn" --region "${AWS_REGION_NAME}")
                if [ $? -eq 0 ]; then
                    expirationDate=$(echo "$tagsResult" | jq -r '.Tags.ExpirationDate')
                    if [ "$expirationDate" != "NEVER" ]; then
                        workspace=$(echo "$tagsResult" | jq -r '.Tags.Workspace')
                        local timestamp=$(python -c "from datetime import datetime, timedelta, timezone; print(format(datetime.now(timezone.utc), '%Y-%m-%dT%H:%M:%SZ'))")
                        local expired=$(python -c "from datetime import datetime, timezone; import sys; print(1) if datetime.strptime('$timestamp', '%Y-%m-%dT%H:%M:%SZ') > datetime.strptime('$expirationDate', '%Y-%m-%dT%H:%M:%SZ') else print(0)")
                        if [ -n "$expirationDate" ] && [ "$expired" = 1 ]; then
                            echo "$workspace"
                            workspaces+=("$workspace")
                        fi
                    fi
                else
                    echo "Error executing get-tags command for $arn"
                fi
            done
        else
            echo "Error executing aws command"
        fi

        # Unset temporary credentials environment variables
        unset AWS_ACCESS_KEY_ID
        unset AWS_SECRET_ACCESS_KEY
        unset AWS_SESSION_TOKEN
    else
        # Print an error message if assume-role command fails
        echo "Error executing aws sts assume-role command"
    fi

    export AWS_ACCESS_KEY_ID="$MGMT_AWS_ACCESS_KEY_ID"
    export AWS_SECRET_ACCESS_KEY="$MGMT_AWS_SECRET_ACCESS_KEY"
    export AWS_SESSION_TOKEN="$MGMT_AWS_SESSION_TOKEN"

    for workspace in "${workspaces[@]}"; do
        echo "Attempting to destroy workspace: $workspace"
        bash ./scripts/infrastructure/terraform/terraform-commands.sh destroy "$ENV" "$workspace" "per_workspace" "-input=false -auto-approve -no-color"
        # Add your additional logic here
    done
}

_destroy_expired_workspaces
