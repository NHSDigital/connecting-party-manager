#!/bin/bash

function _destroy_lambdas() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all Lambda functions and filter the ones containing the substring
    FUNCTIONS=$(aws lambda list-functions | jq -r --arg SUBSTRING "$SUBSTRING" '.Functions[] | select(.FunctionName | contains($SUBSTRING)) | .FunctionName')

    # Check if any functions were found
    if [ -z "$FUNCTIONS" ]; then
        echo "No Lambda functions found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each function
    for FUNCTION_NAME in $FUNCTIONS; do
        echo "Processing Lambda function: $FUNCTION_NAME"

        # List event source mappings for the Lambda function
        EVENT_SOURCE_MAPPINGS=$(aws lambda list-event-source-mappings --function-name "$FUNCTION_NAME" | jq -r '.EventSourceMappings[].UUID')

        # Check if any event source mappings were found
        if [ -z "$EVENT_SOURCE_MAPPINGS" ]; then
            echo "No event source mappings found for Lambda function: $FUNCTION_NAME"
        else
            # Loop through each event source mapping and delete it
            for UUID in $EVENT_SOURCE_MAPPINGS; do
                echo "Deleting event source mapping with UUID: $UUID for Lambda function: $FUNCTION_NAME"
                aws lambda delete-event-source-mapping --uuid "$UUID"
                if [ $? -ne 0 ]; then
                    echo "Failed to delete event source mapping with UUID: $UUID"
                else
                    echo "Successfully deleted event source mapping with UUID: $UUID"
                fi
            done
        fi

        echo "Deleting Lambda function: $FUNCTION_NAME"
        aws lambda delete-function --function-name "$FUNCTION_NAME"
        if [ $? -ne 0 ]; then
            echo "Failed to delete Lambda function: $FUNCTION_NAME"
        else
            echo "Successfully deleted Lambda function: $FUNCTION_NAME"
        fi
    done
}

function _destroy_all_kms() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    ALIASES=$(aws kms list-aliases | jq -r --arg SUBSTRING "$SUBSTRING" '.Aliases[] | select(.AliasName | contains($SUBSTRING)) | .AliasName')

    # Check if any aliases were found
    if [ -z "$ALIASES" ]; then
        echo "No KMS aliases found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each alias and delete it
    for ALIAS in $ALIASES; do

        # Get the KMS key ID associated with the alias
        KEY_ID=$(aws kms describe-key --key-id "$ALIAS" | jq -r '.KeyMetadata.KeyId')

        echo "Deleting KMS alias: $ALIAS"
        aws kms delete-alias --alias-name "$ALIAS"

        # Check if the key ID is valid and then delete the key
        if [ -n "$KEY_ID" ]; then
            echo "Deleting KMS key: $KEY_ID"
            aws kms schedule-key-deletion --key-id "$KEY_ID" --pending-window-in-days 7
        else
            echo "No valid KMS key ID found for alias: $ALIAS"
        fi
    done
}

function _destroy_iam() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all IAM roles and filter those containing the specified substring
    roles=$(aws iam list-roles --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.Roles[] | select(.RoleName | contains($SUBSTRING)) | .RoleName')

    # Check if any roles were found
    if [ -z "$roles" ]; then
        echo "No IAM roles found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each role
    for role in $roles; do
        echo "Processing IAM role: $role"

        # List and detach all managed policies attached to the role
        attached_policies=$(aws iam list-attached-role-policies --role-name "$role" --output json | jq -r '.AttachedPolicies[].PolicyArn')
        for policy_arn in $attached_policies; do
            echo "Detaching managed policy: $policy_arn from role: $role"
            aws iam detach-role-policy --role-name "$role" --policy-arn "$policy_arn"
        done

        # List and delete all inline policies attached to the role
        inline_policies=$(aws iam list-role-policies --role-name "$role" --output json | jq -r '.PolicyNames[]')
        for policy_name in $inline_policies; do
            echo "Deleting inline policy: $policy_name from role: $role"
            aws iam delete-role-policy --role-name "$role" --policy-name "$policy_name"
        done

        # Delete the role itself
        echo "Deleting IAM role: $role"
        aws iam delete-role --role-name "$role"
    done

    echo "Deleted all IAM roles containing the substring: $SUBSTRING"

    # List all IAM policies and filter those containing the specified substring
    policies=$(aws iam list-policies --scope Local --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.Policies[] | select(.PolicyName | contains($SUBSTRING)) | .Arn')

    # Check if any policies were found
    if [ -z "$policies" ]; then
        echo "No IAM policies found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each policy
    for policy_arn in $policies; do
        echo "Deleting IAM policy: $policy_arn"
        aws iam delete-policy --policy-arn "$policy_arn"
    done
}

function _delete_log_groups() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all log groups and filter those containing the specified substring
    log_groups=$(aws logs describe-log-groups | jq -r --arg substring "$SUBSTRING" '.logGroups[] | select(.logGroupName | contains($substring)) | .logGroupName')

    # Check if any log groups were found
    if [ -z "$log_groups" ]; then
        echo "No CloudWatch Logs log groups found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each log group and delete it
    for log_group in $log_groups; do
        echo "Deleting CloudWatch Logs log group: $log_group"
        aws logs delete-log-group --log-group-name "$log_group"
    done
}

function _delete_secrets() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all secrets and filter those containing the specified substring
    secrets=$(aws secretsmanager list-secrets | jq -r --arg substring "$SUBSTRING" '.SecretList[] | select(.Name | contains($substring)) | .ARN')

    # Check if any secrets were found
    if [ -z "$secrets" ]; then
        echo "No Secrets Manager secrets found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each secret and delete it
    for secret in $secrets; do
        echo "Deleting Secrets Manager secret: $secret"
        aws secretsmanager delete-secret --secret-id "$secret" --force-delete-without-recovery
    done
}

function _delete_dynamo_tables() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all DynamoDB tables and filter those containing the specified substring
    tables=$(aws dynamodb list-tables | jq -r --arg substring "$SUBSTRING" '.TableNames[] | select(. | contains($substring))')

    # Check if any tables were found
    if [ -z "$tables" ]; then
        echo "No DynamoDB tables found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each table and delete it
    for table in $tables; do
        echo "Deleting DynamoDB table: $table"
        aws dynamodb delete-table --table-name "$table"
    done
}

function _delete_s3_buckets() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all S3 buckets and filter those containing the specified substring
    buckets=$(aws s3api list-buckets | jq -r '.Buckets[].Name' | grep -- "$SUBSTRING")

    # Check if any buckets were found
    if [ -z "$buckets" ]; then
        echo "No S3 buckets found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each bucket
    for bucket in $buckets; do
        echo "Deleting objects in S3 bucket: $bucket"
        # List all objects (including versions) in the bucket
        objects=$(aws s3api list-object-versions --bucket "$bucket" --output json | jq -r '.Versions[] | {Key: .Key, VersionId: .VersionId}')

        # Loop through each object and delete it
        if [ "$objects" != "[]" ]; then
            echo "$objects" | jq -c '.[]' | while read -r object; do
                aws s3api delete-object --bucket "$bucket" --key "$(echo "$object" | jq -r '.Key')"
            done
        fi

        # Delete all non-current versions
        non_current_versions=$(aws s3api list-object-versions --bucket "$bucket" --output json | jq -r '.DeleteMarkers[] | {Key: .Key, VersionId: .VersionId}')
        for delMarker in $non_current_versions; do
            key=$(echo "$delMarker" | jq -r '.Key')
            versionId=$(echo "$delMarker" | jq -r '.VersionId')

            echo "Deleting non-current version: $key (VersionId: $versionId)"
            aws s3api delete-object --bucket "$bucket" --key "$key" --version-id "$versionId"
        done

        # Delete the bucket
        echo "Deleting S3 bucket: $bucket"
        aws s3 rb "s3://$bucket" --force
    done
}

function _delete_api_gateway() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all APIs
    apis=$(aws apigateway get-rest-apis --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.items[] | select(.name | contains($SUBSTRING)) | .id')

    # Check if any APIs were found
    if [ -z "$apis" ]; then
        echo "No API Gateway resources found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each API
    for api_id in $apis; do
        # List stages for the API
        stages=$(aws apigateway get-stages --rest-api-id "$api_id" --output json | jq -r '.item[].stageName')

        # Loop through each stage and delete base path mappings, deployments, and stages
        for stage in $stages; do
            # List all domain names
            domains=$(aws apigateway get-domain-names --output json | jq -r '.items[].domainName')

            # Loop through each domain and delete base path mappings associated with the specific API and stage
            for domain in $domains; do
                if [[ $domain == *$workspace* ]]; then
                echo "Checking domain: $domain"
                    base_path_mappings=$(aws apigateway get-base-path-mappings --domain-name "$domain" --output json | jq -r --arg STAGE "$stage" --arg API_ID "$api_id" '.items[] | select(.stage == $STAGE and .restApiId == $API_ID) | .basePath')
                    for base_path in $base_path_mappings; do
                        echo "Deleting base path mapping: $base_path in domain: $domain"
                        aws apigateway delete-base-path-mapping --domain-name "$domain" --base-path "$base_path"
                    done
                fi
            done

            # Delete deployments for the stage
            deployment_ids=$(aws apigateway get-deployments --rest-api-id "$api_id" --output json | jq -r '.items[].id')
            for deployment_id in $deployment_ids; do
                echo "Deleting deployment ID: $deployment_id"
                aws apigateway delete-deployment --rest-api-id "$api_id" --deployment-id "$deployment_id"
            done

            # Delete the stage itself
            echo "Deleting stage: $stage"
            aws apigateway delete-stage --rest-api-id "$api_id" --stage-name "$stage"
        done

        # Delete the API itself
        echo "Deleting API: $api_id"
        aws apigateway delete-rest-api --rest-api-id "$api_id"

        # After deleting APIs, delete the domain names
        for domain in $domains; do
            if [[ $domain == *$workspace* ]]; then
                echo "Deleting domain: $domain"
                aws apigateway delete-domain-name --domain-name "$domain"
                if [ $? -ne 0 ]; then
                    echo "Failed to delete domain: $domain"
                else
                    echo "Successfully deleted domain: $domain"
                fi
            fi
        done
    done
}

function _delete_ssm_parameters() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all SSM Parameters
    params=$(aws ssm describe-parameters --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.Parameters[] | select(.Name | contains($SUBSTRING)) | .Name')

    # Check if any Parameters were found
    if [ -z "$params" ]; then
        echo "No SSM Parameters found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each Parameter
    for param in $params; do
        echo "Deleting SSM Parameter: $param"
        aws ssm delete-parameter --name "$param"
    done
}

function _delete_firehose_delivery_streams() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all Firehose delivery streams
    streams=$(aws firehose list-delivery-streams --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.DeliveryStreamNames[] | select(contains($SUBSTRING))')

    # Check if any delivery streams were found
    if [ -z "$streams" ]; then
        echo "No Kinesis Data Firehose delivery streams found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each delivery stream
    for stream in $streams; do
        echo "Deleting Kinesis Data Firehose delivery stream: $stream"
        aws firehose delete-delivery-stream --delivery-stream-name "$stream"
    done
}

function _delete_sqs_queues() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all SQS queues
    queues=$(aws sqs list-queues --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.QueueUrls[] | select(contains($SUBSTRING))')

    # Check if any queues were found
    if [ -z "$queues" ]; then
        echo "No SQS queues found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each queue
    for queue_url in $queues; do
        queue_name=$(basename "$queue_url")
        echo "Deleting SQS queue: $queue_name"
        aws sqs delete-queue --queue-url "$queue_url"
    done
}

function _delete_step_functions() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all Step Functions state machines
    state_machines=$(aws stepfunctions list-state-machines --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.stateMachines[] | select(.name | contains($SUBSTRING)) | .stateMachineArn')

    # Check if any state machines were found
    if [ -z "$state_machines" ]; then
        echo "No Step Functions found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each state machine
    for state_machine_arn in $state_machines; do
        state_machine_name=$(basename "$state_machine_arn")
        echo "Deleting Step Function: $state_machine_name"
        aws stepfunctions delete-state-machine --state-machine-arn "$state_machine_arn"
    done
}

function _delete_cloudwatch_events_rules() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all CloudWatch Events rules
    rules=$(aws events list-rules --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.Rules[] | select(.Name | contains($SUBSTRING)) | .Name')

    # Check if any rules were found
    if [ -z "$rules" ]; then
        echo "No CloudWatch Events rules found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each rule
    for rule_name in $rules; do
        echo "Disabling CloudWatch Events rule: $rule_name"
        aws events disable-rule --name "$rule_name"

        # List targets for the rule
        targets=$(aws events list-targets-by-rule --rule "$rule_name" --output json | jq -r '.Targets[].Id')

        # Remove targets for the rule
        for target_id in $targets; do
            echo "Removing target $target_id from rule: $rule_name"
            aws events remove-targets --rule "$rule_name" --ids "$target_id"
        done

        # Delete the rule itself
        echo "Deleting CloudWatch Events rule: $rule_name"
        aws events delete-rule --name "$rule_name"
    done
}

function _delete_acm_certificates() {
    local workspace=$1
    SUBSTRING="--$workspace--"
    # List all ACM certificates
    certificates=$(aws acm list-certificates --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.CertificateSummaryList[] | select(.DomainName | contains($SUBSTRING)) | .CertificateArn')

    # Check if any certificates were found
    if [ -z "$certificates" ]; then
        echo "No ACM certificates found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each certificate
    for cert_arn in $certificates; do
        echo "Deleting ACM certificate: $cert_arn"
        cert_name=$(aws acm describe-certificate --certificate-arn "$cert_arn" --output json | jq -r '.Certificate.DomainValidationOptions[0].DomainName')
        aws acm delete-certificate --certificate-arn "$cert_arn"
        echo "The certificate may not have deleted, please check and delete manually at https://eu-west-2.console.aws.amazon.com/acm/home?region=eu-west-2#/certificates/$cert_name"
    done

}

function _delete_resource_groups() {
    local workspace=$1
    SUBSTRING="--$workspace--"

    # List all Resource Groups
    resource_groups=$(aws resource-groups list-groups --output json | jq -r --arg SUBSTRING "$SUBSTRING" '.GroupIdentifiers[] | select(.GroupArn | contains($SUBSTRING)) | .GroupName')

    # Check if any Resource Groups were found
    if [ -z "$resource_groups" ]; then
        echo "No Resource Groups found containing the substring: $SUBSTRING"
        return 0
    fi

    # Loop through each Resource Group
    for group_name in $resource_groups; do
        echo "Deleting Resource Group: $group_name"
        aws resource-groups delete-group --group-name "$group_name"
    done
}
