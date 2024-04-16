#!/bin/bash

function _substitute_environment_variables() {
  eval "cat << EOF
$(cat $1)
EOF"
}

AWS_REGION_NAME="eu-west-2"

#
# Check we're not running this against MGMT
#
. "./scripts/aws/helpers.sh"
if _validate_current_account "MGMT"; then
  echo "Please login to non-mgmt profile before running this script"
  exit 1
fi

./scripts/infrastructure/roles/manage-non-mgmt-aws-roles.sh
./scripts/infrastructure/roles/manage-non-mgmt-aws-deployment-policies.sh
./scripts/infrastructure/roles/manage-non-mgmt-aws-support-integration-policies.sh
