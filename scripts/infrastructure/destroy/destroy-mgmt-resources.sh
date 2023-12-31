#!/bin/bash

# Check if the script has received the correct number of arguments
if [ $# -ne 2 ]; then
  echo "Usage: $0 <PREFIX> <VERSION>"
  exit 1
fi

PREFIX="$1"
VERSION="$2"

version_pattern="^v[0-9]+(\.[0-9]+){2}$"

if [[ ! $VERSION =~ $version_pattern ]]; then
    echo "The version '$VERSION' does not conform to any of the allowed pattern."
    exit 1
fi

AWS_REGION_NAME="eu-west-2"
MGMT_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--mgmt-account-id-${VERSION}"
PROD_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--prod-account-id-${VERSION}"
REF_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--ref-account-id-${VERSION}"
INT_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--int-account-id-${VERSION}"
QA_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--qa-account-id-${VERSION}"
DEV_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--dev-account-id-${VERSION}"

admin_policy_arn="arn:aws:iam::aws:policy/AdministratorAccess"
truststore_bucket_name="${PREFIX}--truststore-${VERSION}"
state_bucket_name="${PREFIX}--terraform-state-${VERSION}"
state_lock_table_name="${PREFIX}--terraform-state-lock-${VERSION}"

aws dynamodb delete-table --table-name "${state_lock_table_name}" || exit 1
versioned_objects=NULL
versioned_objects=$(aws s3api list-object-versions \
                    --bucket "${state_bucket_name}" \
                    --output=json \
                    --query='{Objects: Versions[].{Key:Key,VersionId:VersionId}}') || exit 1
aws s3api delete-objects \
    --bucket "${state_bucket_name}" \
    --delete "${versioned_objects}" || echo "Ignore the previous warning - an empty bucket is a good thing"
echo "Waiting for bucket contents to be deleted..." && sleep 10
aws s3 rb "s3://${state_bucket_name}" || echo "Bucket could not be deleted at this time. You should go to the AWS Console and delete the bucket manually."
aws secretsmanager delete-secret --secret-id "${MGMT_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager delete-secret --secret-id "${DEV_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager delete-secret --secret-id "${QA_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager delete-secret --secret-id "${INT_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager delete-secret --secret-id "${REF_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager delete-secret --secret-id "${PROD_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
