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

function _update_policy() {
  policy_name="$1"
  policy_type="$2"
  role_names=("${@:3}")
  aws iam get-policy --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}" &> /dev/null
  if [ $? != 0 ]; then
    tf_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/${policy_type}-policy.json)
    aws iam create-policy \
      --policy-name "${policy_name}" \
      --policy-document "${tf_policy}" \
      --region "${AWS_REGION_NAME}" \
      || exit 1

    for role in "${role_names[@]}"; do
      if [ "${role}" == "NHSDevelopmentRole" ]; then
        if ! _validate_current_account "PROD"; then
          aws iam attach-role-policy \
            --role-name "${role}" \
            --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}" \
            --region "${AWS_REGION_NAME}" \
            || exit 1
        fi
      else
        aws iam attach-role-policy \
          --role-name "${role}" \
          --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}" \
          --region "${AWS_REGION_NAME}" \
          || exit 1
      fi
    done
  else
    for role in "${role_names[@]}"; do
      attached_policies=$(aws iam list-attached-role-policies --role-name "${role}" --region "${AWS_REGION_NAME}")
      if [[ ! $attached_policies == *"\"PolicyName\": \"${policy_name}\""* ]]; then
        if [ "${role}" == "NHSDevelopmentRole" ]; then
          if ! _validate_current_account "PROD"; then
            aws iam attach-role-policy \
              --role-name "${role}" \
              --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}" \
              --region "${AWS_REGION_NAME}" \
              || exit 1
          fi
        else
          aws iam attach-role-policy \
            --role-name "${role}" \
            --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}" \
            --region "${AWS_REGION_NAME}" \
            || exit 1
        fi
      fi
    done

    tf_policy=$(_substitute_environment_variables ./scripts/infrastructure/policies/${policy_type}-policy.json)

    # We update the version because this updates all roles and we don't have to detach and delete.
    versions=$(aws iam list-policy-versions --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}" --region "${AWS_REGION_NAME}")
    num_versions=$(echo "$versions" | jq -r '.Versions | length')
    # There has got to be at least 2 versions.
    if [ "$num_versions" -ge 2 ]; then
      # Extract the oldest version using jq
      oldest_version=$(echo "$versions" | jq -r '.Versions | sort_by(.CreateDate) | .[0].VersionId')

      aws iam delete-policy-version \
        --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}" \
        --version-id "${oldest_version}" \
        || exit 1
    fi

    aws iam create-policy-version \
      --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${policy_name}" \
      --policy-document "${tf_policy}" \
      --set-as-default \
      --region "${AWS_REGION_NAME}" \
      || exit 1
  fi
}

#
# Create the NHSSupportPolicy that will be linked through to SSO for Developer
# and DevOps access We don't need to use a Role, as this Policy will only be
# used in SSO
#
_update_policy "NHSSupportPolicy" "support" "NHSDevelopmentRole"

#
# Create the NHSIntegrationPolicy that will be used for CI Test access
#
_update_policy "NHSIntegrationPolicy" "integration-test" "NHSTestCIRole"
