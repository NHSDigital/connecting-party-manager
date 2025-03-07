#!/bin/bash

function _substitute_environment_variables() {
  eval "cat << EOF
$(cat $1)
EOF"
}

AWS_REGION_NAME="eu-west-2"
ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account)

ENV="dev"

#
# Check we're not running this against MGMT
#
. "./scripts/aws/helpers.sh"
if _validate_current_account "MGMT"; then
  echo "Please login to non-mgmt profile before running this script"
  exit 1
else
  if _validate_current_account "PROD"; then
    ENV="prod"
  elif _validate_current_account "INT"; then
    ENV="int"
  elif _validate_current_account "QA"; then
    ENV="qa"
  elif _validate_current_account "INT"; then
    ENV="int"
  elif _validate_current_account "REF"; then
    ENV="ref"
  fi
fi
EXTERNAL_ID_PARAMETER_STORE="${ENV}-external-id"
MGMT_ID_PARAMETER_STORE="nhse-cpm--${ENV}--mgmt-account-id-v1.0.0"

EXTERNAL_ID=$(aws secretsmanager get-secret-value --secret-id "$EXTERNAL_ID_PARAMETER_STORE" --region "$AWS_REGION_NAME" --query 'SecretString' --output text)
MGMT_ACCOUNT_ID=$(aws secretsmanager get-secret-value --secret-id "$MGMT_ID_PARAMETER_STORE" --region "$AWS_REGION_NAME" --query 'SecretString' --output text)

tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/role-trust-policy.json)
aws iam update-assume-role-policy --role-name NHSDeploymentRole --policy-document "${tf_assume_role_policy}"
aws iam update-assume-role-policy --role-name NHSSmokeTestRole --policy-document "${tf_assume_role_policy}"

if [ "$ENV" != "prod" ]; then
  aws iam update-assume-role-policy --role-name NHSDevelopmentRole --policy-document "${tf_assume_role_policy}"
  aws iam update-assume-role-policy --role-name NHSTestCIRole --policy-document "${tf_assume_role_policy}"
fi
