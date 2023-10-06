#!/bin/bash

# Check if the script has received the correct number of arguments
if [ $# -ne 2 ]; then
  echo "Usage: $0 <PREFIX> <VERSION>"
  exit 1
fi

PREFIX="$1"
VERSION="$2"

# version_pattern="^v(?:[0-9]|[1-9][0-9]{0,2})\.(?:[0-9]|[1-9][0-9]?)\.(?:[0-9]|[1-9][0-9]?)$"
# version_pattern="^v(?:[0-9]|[1-9][0-9]{0,2})\.(?:[0-9]|[1-9][0-9]?)\.(?:[0-9]|[1-9][0-9]?)$"
version_pattern="^v[0-9]+(\.[0-9]+){2}$"

if [[ ! $VERSION =~ $version_pattern ]]; then
    echo "The version '$VERSION' does not conform to any of the allowed pattern."
    exit 1
fi

AWS_REGION_NAME="eu-west-2"
MGMT_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--mgmt-account-id"
PROD_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--prod-account-id"
TEST_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--test-account-id"
DEV_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--dev-account-id"

admin_policy_arn="arn:aws:iam::aws:policy/AdministratorAccess"
truststore_bucket_name="${PREFIX}--truststore-${VERSION}"
state_bucket_name="${PREFIX}--terraform-state-${VERSION}"
state_lock_table_name="${PREFIX}--terraform-state-lock-${VERSION}"

aws s3api create-bucket --bucket "${truststore_bucket_name}" --region us-east-1 --create-bucket-configuration LocationConstraint="${AWS_REGION_NAME}"
aws s3api create-bucket --bucket "${state_bucket_name}" --region us-east-1 --create-bucket-configuration LocationConstraint="${AWS_REGION_NAME}"
aws s3api put-public-access-block --bucket "${state_bucket_name}" --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
aws dynamodb create-table --region "${AWS_REGION_NAME}" --table-name "${state_lock_table_name}" --attribute-definitions AttributeName=LockID,AttributeType=S \
--key-schema AttributeName=LockID,KeyType=HASH \
--provisioned-throughput ReadCapacityUnits=20,WriteCapacityUnits=20
aws secretsmanager create-secret --name "${MGMT_ACCOUNT_ID_LOCATION}"
aws secretsmanager create-secret --name "${DEV_ACCOUNT_ID_LOCATION}"
aws secretsmanager create-secret --name "${TEST_ACCOUNT_ID_LOCATION}"
aws secretsmanager create-secret --name "${PROD_ACCOUNT_ID_LOCATION}"
