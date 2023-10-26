#!/bin/bash

AWS_REGION_NAME="eu-west-2"
admin_policy_arn="arn:aws:iam::aws:policy/AdministratorAccess"

ACCOUNT_ID=$(aws sts get-caller-identity | jq -r .Account)

aws iam delete-role \
  --role-name "NHSDeploymentRole" \
  || exit 1

aws iam delete-policy \
  --policy-awn "arn:aws:iam::${ACCOUNT_ID}:policy/NHSDeploymentPolicy" \
  || exit 1

echo "Deleted role NHSDeploymentRole and NHSDeploymentPolicy"

aws iam delete-role \
  --role-name "NHSSupportRole" \
  || exit 1

aws iam delete-policy \
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/NHSSupportPolicy" \
  --region "${AWS_REGION_NAME}" \
  || exit 1

echo "Deleted NHSSupportPolicy"
