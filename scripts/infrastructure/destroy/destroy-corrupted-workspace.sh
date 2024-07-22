#!/bin/bash

source ./scripts/infrastructure/destroy/destroy-workspace-utils.sh
source ./scripts/infrastructure/terraform/terraform-constants.sh
source ./scripts/infrastructure/terraform/terraform-utils.sh
source ./scripts/infrastructure/terraform/terraform-commands.sh

TERRAFORM_WORKSPACE="$1"
AWS_REGION_NAME="eu-west-2"
ENV="dev"
persistent_list=("dev" "qa" "int" "ref" "prod")

function _destroy_corrupted_workspace() {
    if [[ "$(aws account get-contact-information --region "${AWS_REGION_NAME}")" != *MGMT* ]]; then
        echo "Please log in as the mgmt account" >&2
        return 1
    fi

    ter_env=$(echo "$TERRAFORM_WORKSPACE" | tr '[:upper:]' '[:lower:]')

    if [[ " ${persistent_list[@]} " =~ "$ter_env" ]]; then
        echo "Workspace cannot be destroyed. Exiting."
        return 1
    fi

    dev_acct=$(_get_aws_account_id "$ENV" "$PROFILE_PREFIX" "$VERSION")
    role_arn="arn:aws:iam::${dev_acct}:role/${TERRAFORM_ROLE_NAME}"
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

        local workspace
        workspace=$TERRAFORM_WORKSPACE
        local cert_name

        _destroy_lambdas "$workspace"
        _destroy_all_kms "$workspace"
        _delete_log_groups "$workspace"
        _delete_secrets "$workspace"
        _delete_s3_buckets "$workspace"
        _delete_dynamo_tables "$workspace"
        _delete_api_gateway "$workspace"
        _delete_ssm_parameters "$workspace"
        _delete_firehose_delivery_streams "$workspace"
        _delete_sqs_queues "$workspace"
        _delete_step_functions "$workspace"
        _delete_cloudwatch_events_rules "$workspace"
        _delete_acm_certificates "$workspace"
        _destroy_iam "$workspace"
        _delete_resource_groups "$workspace"

    else
        # Print an error message if assume-role command fails
        echo "Error executing aws sts assume-role command"
    fi

    echo "The resources have been removed from the dev environment for the ${TERRAFORM_WORKSPACE} workspace. Please run 'make terraform--destroy' to remove the state file from mgmt."

    export AWS_ACCESS_KEY_ID="$MGMT_AWS_ACCESS_KEY_ID"
    export AWS_SECRET_ACCESS_KEY="$MGMT_AWS_SECRET_ACCESS_KEY"
    export AWS_SESSION_TOKEN="$MGMT_AWS_SESSION_TOKEN"

}

_destroy_corrupted_workspace
