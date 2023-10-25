#!/bin/bash

# Check if the script has received the correct number of arguments
if [ $# -ne 1 ]; then
  echo "Usage: $0 <MGMT_ACCOUNT_ID>"
  exit 1
fi

function _substitute_environment_variables() {
  eval "cat << EOF
$(cat $1)
EOF"
}

MGMT_ACCOUNT_ID="$1"
AWS_REGION_NAME="eu-west-2"

#
# Check we're not running this against MGMT
#

ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account)
if [ "$MGMT_ACCOUNT_ID" == "$ACCOUNT_ID" ]; then
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
# Create the NHSDeploymentPolicy that will be used for Developer access and
# NHSDeploymentRole (above)
#

aws iam get-policy --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/NHSDeploymentPolicy" &> /dev/null
if [ $? != 0 ]; then
  tf_deployment_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/deployment-policy.json)

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
# Create the NHSSupportPolicy that will be linked through to SSO for Developer
# and DevOps access We don't need to use a Role, as this Policy will only be
# used in SSO
#

aws iam get-policy --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/NHSSupportPolicy" &> /dev/null
if [ $? != 0 ]; then
  tf_devops_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/support-policy.json)

  aws iam create-policy \
    --policy-name "NHSSupportPolicy" \
    --policy-document "${tf_devops_policy}" \
    --region "${AWS_REGION_NAME}" \
    || exit 1
fi
