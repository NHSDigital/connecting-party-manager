#!/bin/bash

function _substitute_environment_variables() {
  eval "cat << EOF
$(cat $1)
EOF"
}

AWS_REGION_NAME="eu-west-2"
ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account)

#
# Check we're not running this against MGMT
#
. "./scripts/aws/helpers.sh"
if ! _validate_current_account "MGMT"; then
  echo "Please login to non-mgmt profile before running this script"
  exit 1
fi

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
if [ "$PROD_ACCOUNT_ID" != "$ACCOUNT_ID" ]; then
  aws iam get-role --role-name "NHSDevelopmentRole" &> /dev/null
  if [ $? != 0 ]; then
    tf_assume_role_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/role-trust-policy.json)

    aws iam create-role \
      --role-name "NHSDevelopmentRole" \
      --assume-role-policy-document "${tf_assume_role_policy}" \
      --region "${AWS_REGION_NAME}" \
      || exit 1
  fi
fi
