#!/bin/bash

# Check if the script has received the correct number of arguments
if [ $# -ne 2 ]; then
  echo "Usage: $0 <TERRAFORM_ROLE_NAME>"
  exit 1
fi

TERRAFORM_ROLE_NAME="$1"

AWS_REGION_NAME="eu-west-2"
admin_policy_arn="arn:aws:iam::aws:policy/AdministratorAccess"

aws iam detach-role-policy --policy-arn "${admin_policy_arn}" --role-name "${TERRAFORM_ROLE_NAME}" || exit 1
aws iam delete-role --role-name "${TERRAFORM_ROLE_NAME}" || exit 1
echo "Deleted role ${TERRAFORM_ROLE_NAME} and associated policy ${admin_policy_arn}"
