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
if _validate_current_account "MGMT"; then
  echo "Please login to non-mgmt profile before running this script"
  exit 1
fi

#
# Create the NHSDeploymentPolicy that will be used for Developer access and
# NHSDeploymentRole. This policy is split into 2 as the file size was too large.
#

policy_name="NHSDeploymentPolicy"
role_name="NHSDeploymentRole"

attached_policies=$(aws iam list-attached-role-policies --role-name "${role_name}" --region "${AWS_REGION_NAME}")

for policy_number in "1" "2"; do
  tf_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/deployment${policy_number}-policy.json)
  aws iam get-policy --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}${policy_number}" &> /dev/null
  if [ $? != 0 ]; then
    aws iam create-policy \
      --policy-name "${policy_name}${policy_number}" \
      --policy-document "${tf_policy}" \
      --region "${AWS_REGION_NAME}" \
      || exit 1
    fi
  # We update the version because this updates all roles and we don't have to detach and delete.
  versions=$(aws iam list-policy-versions --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}${policy_number}" --region "${AWS_REGION_NAME}")
  num_versions=$(echo "$versions" | jq -r '.Versions | length')
  # There has got to be at least 2 versions.
  if [ "$num_versions" -ge 2 ]; then
    # Extract the oldest version using jq
    oldest_version=$(echo "$versions" | jq -r '.Versions | sort_by(.CreateDate) | .[0].VersionId')

    aws iam delete-policy-version \
      --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}${policy_number}" \
      --version-id "${oldest_version}" \
      || exit 1
  fi

    aws iam create-policy-version \
      --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}${policy_number}" \
      --policy-document "${tf_policy}" \
      --set-as-default \
      --region "${AWS_REGION_NAME}" \
      || exit 1
  if [[ ! $attached_policies == *"\"PolicyName\": \"${policy_name}${policy_number}\""* ]]; then
    aws iam attach-role-policy \
      --role-name "${role_name}" \
      --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}${policy_number}" \
      --region "${AWS_REGION_NAME}" \
      || exit 1
    fi
done
