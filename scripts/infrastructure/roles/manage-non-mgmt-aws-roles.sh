#!/bin/bash

function _substitute_environment_variables() {
  eval "cat << EOF
$(cat $1)
EOF"
}

AWS_REGION_NAME="eu-west-2"
ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account)


SECRET_MGMT="nhse-cpm--dev--mgmt-account-id-v1.0.0"


#
# Check we're not running this against MGMT
#
. "./scripts/aws/helpers.sh"
if _validate_current_account "MGMT"; then
  echo "Please login to non-mgmt profile before running this script"
  exit 1
fi

if aws secretsmanager describe-secret --secret-id "$SECRET_MGMT" --region "$AWS_REGION_NAME" &> /dev/null; then
  # Secret exists, retrieve its value
  MGMT_ACCOUNT_ID=$(aws secretsmanager get-secret-value --secret-id "$SECRET_MGMT" --region "$AWS_REGION_NAME" --query 'SecretString' --output text)

  #
  # Create the NHSDeploymentRole that will be used for deployment and CI/CD
  #
  aws iam get-role --role-name "NHSDeploymentRole" &> /dev/null
  if [ $? != 0 ]; then
    tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/role-trust-policy.json)

    aws iam create-role \
      --role-name "NHSDeploymentRole" \
      --assume-role-policy-document "${tf_assume_role_policy}" \
      --region "${AWS_REGION_NAME}" \
      || exit 1
  fi
  #
  # Create the NHSDevelopmentRole that will be used for deployment from local environments
  #
  if ! _validate_current_account "PROD"; then
    aws iam get-role --role-name "NHSDevelopmentRole" &> /dev/null
    if [ $? != 0 ]; then
      tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/role-trust-policy.json)

      aws iam create-role \
        --role-name "NHSDevelopmentRole" \
        --assume-role-policy-document "${tf_assume_role_policy}" \
        --region "${AWS_REGION_NAME}" \
        || exit 1
    fi

    aws iam get-role --role-name "NHSIntegrationRole" &> /dev/null
    if [ $? != 0 ]; then
      tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/role-trust-policy.json)

      aws iam create-role \
        --role-name "NHSIntegrationRole" \
        --assume-role-policy-document "${tf_assume_role_policy}" \
        --region "${AWS_REGION_NAME}" \
        || exit 1
    fi
  fi
else
  # Secret doesn't exist, create it with an empty string value
  echo "Secret ${SECRET_MGMT} doesn't exist. Creating..."
  aws secretsmanager create-secret --name "$SECRET_MGMT" --region "$AWS_REGION_NAME" --secret-string "TEMP_VALUE"
  echo "Secret created with an empty string value. Please update it's value and run this script again."
  exit 1
fi
