#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-constants.sh
source ./scripts/infrastructure/terraform/terraform-utils.sh
source ./scripts/infrastructure/terraform/terraform-commands.sh

TERRAFORM_ENVIRONMENT="$1"
AWS_REGION_NAME="eu-west-2"
ENV="dev"
persistent_list=("dev" "int" "ref" "uat" "prod")

function _destroy_corrupted_workspace() {
    if [[ "$(aws account get-contact-information --region "${AWS_REGION_NAME}")" != *MGMT* ]]; then
        echo "Please log in as the mgmt account" >&2
        return 1
    fi

    ter_env=$(echo "$TERRAFORM_ENVIRONMENT" | tr '[:upper:]' '[:lower:]')

    if [[ " ${persistent_list[@]} " =~ "$ter_env" ]]; then
        echo "Workspace cannot be destroyed. Exiting."
        return 1
    fi

    dev_acct=$(_get_aws_account_id "$ENV")
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
        workspace=$TERRAFORM_ENVIRONMENT
        # Fetch the resources using the AWS CLI command
        aws resourcegroupstaggingapi get-resources --tag-filters Key=Workspace,Values="$workspace" | jq -c '.ResourceTagMappingList[]' |
        while IFS= read -r item; do
            arn=$(jq -r '.ResourceARN' <<< "$item")

            case $arn in
                arn:aws:lambda* )
                    echo "Deleting... : $arn"
                    aws lambda delete-function --function-name $arn
                    ;;
                arn:aws:kms* )
                    echo "Disabling... : $arn"
                    aws kms disable-key --key-id $arn
                    echo "Deleting... ': $arn"
                    aws kms schedule-key-deletion --key-id $arn --pending-window-in-days 7
                    ;;
                arn:aws:logs* )
                    echo "Deleting... : $arn"
                    new_var=$(echo "$arn" | awk -F':' '{print $NF}')
                    aws logs delete-log-group --log-group-name $new_var
                    ;;
                arn:aws:secretsmanager* )
                    echo "Deleting... : $arn"
                    aws secretsmanager delete-secret --secret-id $arn
                    ;;
                arn:aws:apigateway* )
                        echo "Deleting domain-name... : $workspace"
                        aws apigateway delete-domain-name --domain-name "$workspace.api.record-locator.dev.national.nhs.uk"
                        echo "Deleting... : $arn"
                        ag_id=$(echo "$arn" | awk -F'/restapis/' '{print $2}' | awk -F'/' '{print $1}')
                        aws apigateway delete-rest-api --rest-api-id $ag_id
                    ;;
                arn:aws:dynamodb* )
                    echo "Deleting... : $arn"
                    new_var=$(echo "$arn" | awk -F':' '{print $NF}')
                    table=$(echo "$arn" | awk -F'/' '{print $NF}')
                    aws dynamodb delete-table --table-name $table
                    ;;
                arn:aws:s3* )
                    echo "Deleting... : $arn"
                    new_var=$(echo "$arn" | awk -F':' '{print $NF}')
                    local versioned_objects
                    versioned_objects=$(aws s3api list-object-versions \
                                        --bucket "${new_var}" \
                                        --output=json \
                                        --query='{Objects: Versions[].{Key:Key,VersionId:VersionId}}') || return 1
                    aws s3api delete-objects \
                        --bucket "${new_var}" \
                        --delete "${versioned_objects}" || echo "Ignore the previous warning - an empty bucket is a good thing"
                    echo "Waiting for bucket contents to be deleted..." && sleep 10
                    aws s3 rb "s3://${new_var}" --force || echo "Bucket could not be deleted at this time. You should go to the AWS Console and delete the bucket manually."
                    ;;
                arn:aws:ssm* )
                    echo "Deleting... : $arn"
                    new_var=$(echo "$arn" | awk -F':' '{print $NF}')
                    suffix=$(echo "$arn" | awk -F'/' '{print $NF}')
                    name=$(echo "$new_var" | awk -F'/' '{print $(NF-1)}')
                    aws ssm delete-parameter --name $name/$suffix
                    ;;
                arn:aws:acm* )
                    echo "Deleting... : $arn"
                    aws acm delete-certificate --certificate-arn $arn
                    ;;
                arn:aws:firehose* )
                    echo "Deleting... : $arn"
                    new_var=$(echo "$arn" | awk -F':' '{print $NF}')
                    name=$(echo "$new_var" | awk -F'/' '{print $NF}')
                    aws firehose delete-delivery-stream --delivery-stream-name $name
                    ;;
                * )
                    echo "Unknown ARN type: $arn"
                    ;;
            esac
        done
    else
        # Print an error message if assume-role command fails
        echo "Error executing aws sts assume-role command"
    fi

    echo "The resources have been removed from the dev environment for the ${TERRAFORM_ENVIRONMENT} workspace. Please now remove it from the s3 and lock table manually on MGMT."

    export AWS_ACCESS_KEY_ID="$MGMT_AWS_ACCESS_KEY_ID"
    export AWS_SECRET_ACCESS_KEY="$MGMT_AWS_SECRET_ACCESS_KEY"
    export AWS_SESSION_TOKEN="$MGMT_AWS_SESSION_TOKEN"
}

_destroy_corrupted_workspace
