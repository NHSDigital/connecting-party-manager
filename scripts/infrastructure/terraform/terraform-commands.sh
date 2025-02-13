#!/bin/bash

source ./scripts/infrastructure/terraform/terraform-utils.sh

TERRAFORM_COMMAND="$1"
AWS_ACCOUNT="$2"
TERRAFORM_WORKSPACE="$3"
TERRAFORM_SCOPE="$4"
TERRAFORM_ARGS="$5"
AWS_REGION_NAME="eu-west-2"

function _terraform() {
  local workspace
  local aws_account_id
  local var_file
  local current_date
  local terraform_dir
  local expiration_time
  local terraform_role_name="NHSDeploymentRole"
  lowercase_string=$(echo "$TERRAFORM_WORKSPACE" | tr '[:upper:]' '[:lower:]')

  account=$(_get_account_name "$AWS_ACCOUNT") || return 1
  workspace=$(_get_workspace_name "$account" "$lowercase_string") || return 1
  aws_account_id=$(_get_aws_account_id "$account" "$PROFILE_PREFIX" "$VERSION") || return 1

  var_file=$(_get_workspace_vars_file "$account") || return 1
  scope=$(_get_terraform_scope "$TERRAFORM_SCOPE") || return 1
  terraform_dir=$(_get_terraform_dir "$scope") || return 1
  workspace_type=$(_get_workspace_type "$account" "$workspace")
  workspace_expiration=$(_get_workspace_expiration "$workspace_type")
  expiration_date=$(_get_expiration_date "$workspace_expiration")
  current_date=$(_get_current_date) || return 1
  layers=$(_get_layer_list) || return 1
  third_party_layers=$(_get_third_party_layer_list) || return 1
  lambdas=$(_get_lambda_list) || return 1
  login_account=$(_get_account_full_name) || return 1
  local plan_file="./tfplan"

  if [[ "${TERRAFORM_COMMAND}" != "clean" ]]; then
    echo "
        Terraforming
        -------------------- ----------------------------------------
        login_account        ${login_account}
        scope                ${scope}
        account              ${account}
        raw_workspace        ${TERRAFORM_WORKSPACE}
        workspace            ${workspace}
        workspace_type       ${workspace_type}
        workspace_expiration ${workspace_expiration}
        expiration_date      ${expiration_date}
        role                 ${terraform_role_name}

        third_party_layers ${layers}
        third_party_layers ${third_party_layers}
    "
  fi

  if [[ "${login_account}" != "NHS Digital Spine Core CPM MGMT" ]]; then
    echo "Please log in as the mgmt account" >&2
    return 1
  fi

  cd "$terraform_dir" || return 1

  case $TERRAFORM_COMMAND in
  #----------------
  "validate")
    terraform validate || return 1
    ;;
  #----------------
  "init")
    _terraform_init "$workspace" "$TERRAFORM_ARGS"
    ;;
  #----------------
  "plan")
    _terraform_plan "$workspace" "$var_file" "$plan_file" "$aws_account_id" "$scope" "$TERRAFORM_ARGS"
    ;;
  #----------------
  "apply")
    _terraform_apply "$workspace" "$plan_file" "$TERRAFORM_ARGS"
    ;;
  #----------------
  "destroy")
    _terraform_destroy "$workspace" "$var_file" "$aws_account_id" "$TERRAFORM_ARGS"
    ;;
  #----------------
  "unlock")
    TF_WORKSPACE=$workspace _terraform_unlock "$TERRAFORM_ARGS"
    ;;
  #----------------
  "clean")
    terraform workspace select default
    ;;
  esac
}
function _terraform_init() {
  local workspace=$1
  local args=${@:2}
  terraform workspace select default
  terraform init $args || return 1
  terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1
}

function _terraform_plan() {
  local workspace=$1
  local var_file=$2
  local plan_file=$3
  local aws_account_id=$4
  local scope=$5

  local args=${@:6}

  terraform workspace select default
  terraform init || return 1
  terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1

if [[ "${scope}" =~ ^per_workspace/.*$ ]]; then
    terraform plan $args \
      -out="$plan_file" \
      -var-file="$var_file" \
      -var "assume_account=${aws_account_id}" \
      -var "assume_role=${terraform_role_name}" \
      -var "updated_date=${current_date}" \
      -var "expiration_date=${expiration_date}" \
      -var "lambdas=${lambdas}" \
      -var "workspace_type=${workspace_type}" \
      -var "layers=${layers}" \
      -var "third_party_layers=${third_party_layers}" || return 1
  else
    terraform plan $args \
      -out="$plan_file" \
      -var-file="$var_file" \
      -var "assume_account=${aws_account_id}" \
      -var "assume_role=${terraform_role_name}" \
      -var "updated_date=${current_date}" \
      -var "expiration_date=${expiration_date}" || return 1
  fi
}

function _terraform_apply() {
  local workspace=$1
  local plan_file=$2
  local args=${@:3}

  echo $workspace

  terraform init || return 1
  terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1
  terraform apply $args "$plan_file" || return 1
  terraform output -json >output.json || return 1
}

function _terraform_destroy() {
  local workspace=$1
  local var_file=$2
  local aws_account_id=$3
  local args=${@:4}

  terraform init -reconfigure || return 1
  terraform workspace select "$workspace" || terraform workspace new "$workspace" || return 1

  terraform apply -destroy $args \
    -var-file="$var_file" \
    -var "assume_account=${aws_account_id}" \
    -var "assume_role=${terraform_role_name}" \
    -var "workspace_type=${workspace_type}" \
    -var "lambdas=${lambdas}" \
    -var "layers=${layers}" \
    -var "third_party_layers=${third_party_layers}" ||
    return 1

  if [ "$workspace" != "default" ]; then
    terraform workspace select default || return 1
    terraform workspace delete "$workspace" || return 1
  fi
}

function _terraform_unlock() {
  local workspace=$1
  terraform force-unlock "$workspace"
}

_terraform $@
