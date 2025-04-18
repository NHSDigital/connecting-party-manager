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
  elif _validate_current_account "Backups"; then
    ENV="backups"
  fi
fi
MGMT_ID_PARAMETER_STORE="nhse-cpm--${ENV}--mgmt-account-id-v1.0.0"
EXTERNAL_ID_PARAMETER_STORE="${ENV}-external-id"
if aws secretsmanager describe-secret --secret-id "$MGMT_ID_PARAMETER_STORE" --region "$AWS_REGION_NAME" &>/dev/null; then
  # Secret exists, retrieve its value
  MGMT_ACCOUNT_ID=$(aws secretsmanager get-secret-value --secret-id "$MGMT_ID_PARAMETER_STORE" --region "$AWS_REGION_NAME" --query 'SecretString' --output text)
  EXTERNAL_ID=$(aws secretsmanager get-secret-value --secret-id "$EXTERNAL_ID_PARAMETER_STORE" --region "$AWS_REGION_NAME" --query 'SecretString' --output text)
  #
  # Create the NHSDeploymentRole that will be used for deployment and CI/CD in All Deployment environments
  #
  aws iam get-role --role-name "NHSDeploymentRole" &>/dev/null
  if [ $? != 0 ]; then
    tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/role-trust-policy.json)

    aws iam create-role \
      --role-name "NHSDeploymentRole" \
      --assume-role-policy-document "${tf_assume_role_policy}" \
      --region "${AWS_REGION_NAME}" ||
      exit 1
  fi

  #
  # Create the NHSSmokeTestRole that will be used for smoke tests in All Deployment environments
  #
  if ! _validate_current_account "Backups"; then
    aws iam get-role --role-name "NHSSmokeTestRole" &> /dev/null
    if [ $? != 0 ]; then
      tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/role-trust-policy.json)

    aws iam create-role \
      --role-name "NHSSmokeTestRole" \
      --assume-role-policy-document "${tf_assume_role_policy}" \
      --region "${AWS_REGION_NAME}" ||
      exit 1
  fi

  #
  # Create the NHSDevelopmentRole that will be used for deployment from local environments
  #
  if [ ! $(_validate_current_account "PROD") ] && [ ! $(_validate_current_account "Backups") ]; then
    aws iam get-role --role-name "NHSDevelopmentRole" &> /dev/null
    if [ $? != 0 ]; then
      tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/role-trust-policy.json)

      aws iam create-role \
        --role-name "NHSDevelopmentRole" \
        --assume-role-policy-document "${tf_assume_role_policy}" \
        --region "${AWS_REGION_NAME}" ||
        exit 1
    fi

    aws iam get-role --role-name "NHSTestCIRole" &>/dev/null
    if [ $? != 0 ]; then
      tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/role-trust-policy.json)

      aws iam create-role \
        --role-name "NHSTestCIRole" \
        --assume-role-policy-document "${tf_assume_role_policy}" \
        --region "${AWS_REGION_NAME}" ||
        exit 1
    fi
  fi
else
  # Secret doesn't exist, create it with an empty string value
  echo "Secret ${MGMT_ID_PARAMETER_STORE} doesn't exist. Creating..."
  aws secretsmanager create-secret --name "$MGMT_ID_PARAMETER_STORE" --region "$AWS_REGION_NAME" --secret-string "TEMP_VALUE"
  echo "Secret created with an empty string value. Please update it's value and run this script again."
  exit 1
fi
