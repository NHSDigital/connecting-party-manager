#!/bin/bash

# Check if the script has received the correct number of arguments
if [ $# -ne 2 ]; then
  echo "Usage: $0 <MGMT_ACCOUNT_ID> <TERRAFORM_ROLE_NAME>"
  exit 1
fi

MGMT_ACCOUNT_ID="$1"
TERRAFORM_ROLE_NAME="$2"

AWS_REGION_NAME="eu-west-2"
admin_policy_arn="arn:aws:iam::aws:policy/AdministratorAccess"

tf_assume_role_policy=NULL
tf_assume_role_policy=$(awk "{sub(/REPLACEME/,\"${MGMT_ACCOUNT_ID}\")}1" role-trust-policy.json)
aws iam create-role --role-name "${TERRAFORM_ROLE_NAME}" --assume-role-policy-document "${tf_assume_role_policy}" --region "${AWS_REGION_NAME}" || return 1
aws iam attach-role-policy --policy-arn "${admin_policy_arn}" --role-name "${TERRAFORM_ROLE_NAME}" --region "${AWS_REGION_NAME}" || return 1
