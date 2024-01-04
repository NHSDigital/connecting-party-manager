#!/bin/bash

function _substitute_environment_variables() {
  eval "cat << EOF
$(cat $1)
EOF"
}

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

ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account)
AWS_REGION_NAME="eu-west-2"
MGMT_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--mgmt-account-id-${VERSION}"
DEV_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--dev-account-id-${VERSION}"
PROD_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--prod-account-id-${VERSION}"
QA_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--qa-account-id-${VERSION}"
INT_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--int-account-id-${VERSION}"
REF_ACCOUNT_ID_LOCATION="${PREFIX}--mgmt--ref-account-id-${VERSION}"

admin_policy_arn="arn:aws:iam::aws:policy/AdministratorAccess"
truststore_bucket_name="${PREFIX}--truststore-${VERSION}"
state_bucket_name="${PREFIX}--terraform-state-${VERSION}"
state_lock_table_name="${PREFIX}--terraform-state-lock-${VERSION}"

#
# Create the NHSDeploymentRole that will be used for deployment and CI/CD
#

aws iam get-role --role-name "NHSDeploymentRole" &> /dev/null
if [ $? != 0 ]; then
  tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/mgmt-role-trust-policy.json)

  aws iam create-role \
    --role-name "NHSDeploymentRole" \
    --assume-role-policy-document "${tf_assume_role_policy}" \
    --region "${AWS_REGION_NAME}" \
    || exit 1
fi

#
# Create the NHSDeploymentPolicy that will be used for Developer access and CI/CD
#

aws iam get-policy --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/NHSDeploymentPolicy" &> /dev/null
if [ $? != 0 ]; then
  tf_deployment_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/mgmt-deployment-policy.json)

  aws iam create-policy \
    --policy-name "NHSDeploymentPolicy" \
    --policy-document "${tf_deployment_policy}" \
    --region "${AWS_REGION_NAME}" \
    || exit 1
fi

aws iam attach-role-policy \
  --role-name "NHSDeploymentRole" \
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/NHSDeploymentPolicy" \
  --region "${AWS_REGION_NAME}" \
  || exit 1

#
# Create the NHSSupportPolicy that will be used for Support access
#

aws iam get-policy --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/NHSSupportPolicy" &> /dev/null
if [ $? != 0 ]; then
  tf_support_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/mgmt-support-policy.json)

  aws iam create-policy \
    --policy-name "NHSSupportPolicy" \
    --policy-document "${tf_support_policy}" \
    --region "${AWS_REGION_NAME}" \
    || exit 1
fi

#
# Create the Trust Store bucket
#

aws s3api create-bucket \
  --bucket "${truststore_bucket_name}" \
  --region us-east-1 \
  --create-bucket-configuration LocationConstraint="${AWS_REGION_NAME}"

#
# Create the Terraform state bucket
#

aws s3api create-bucket \
  --bucket "${state_bucket_name}" \
  --region us-east-1 \
  --create-bucket-configuration LocationConstraint="${AWS_REGION_NAME}"

aws s3api put-public-access-block \
  --bucket "${state_bucket_name}" \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

#
# Create the Terraform lock table
#


aws dynamodb create-table \
  --region "${AWS_REGION_NAME}" \
  --table-name "${state_lock_table_name}" \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=20,WriteCapacityUnits=20

#
# Create the secrets for storing account IDs.
#

aws secretsmanager create-secret --name "${MGMT_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager create-secret --name "${DEV_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager create-secret --name "${QA_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager create-secret --name "${INT_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager create-secret --name "${REF_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
aws secretsmanager create-secret --name "${PROD_ACCOUNT_ID_LOCATION}" --region "${AWS_REGION_NAME}"
