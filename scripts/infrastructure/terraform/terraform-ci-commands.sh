!/bin/bash

source ./scripts/infrastructure/terraform/terraform-constants.sh
source ./scripts/infrastructure/terraform/terraform-utils.sh
source ./scripts/infrastructure/terraform/terraform-ci-commands.sh

TERRAFORM_COMMAND="$1"
TERRAFORM_ENVIRONMENT="$2"
TERRAFORM_ACCOUNT_WIDE="$3"
TERRAFORM_ARGS="$4"
AWS_REGION_NAME="eu-west-2"

function _terraform_ci() {
    local account_wide=$3
    local env
    local aws_account_id
    local var_file
    local current_timestamp
    local terraform_dir
    env=$(_get_environment_name $TERRAFORM_ENVIRONMENT)
    aws_account_id=$(_get_aws_account_id "$env")
    var_file=$(_get_environment_vars_file "$env")
    terraform_dir=$(_get_terraform_dir "$env" "$TERRAFORM_ACCOUNT_WIDE")
    current_timestamp="$(date '+%Y_%m_%d__%H_%M_%S')"
    local plan_file="./tfplan"
    local ci_log_bucket="${PROJECT_PREFIX}-mgmt--github-ci-logging"

    case $TERRAFORM_COMMAND in
        "ci-init")
            if [[ "$RUNNING_IN_CI" != 1 ]]; then
                echo "Command should only be used by CI pipeline" >&2
                return 1
            fi

            echo "Init terraform for aws workspace: ${env}"

            local tf_init_output="${env}-tf-init-output_${current_timestamp}.txt"

            cd "$terraform_dir" || return 1
            _terraform_init "$env" |& tee "./${tf_init_output}" > /dev/null
            local tf_init_status="${PIPESTATUS[0]}"
            aws s3 cp "./${tf_init_output}" "s3://${ci_log_bucket}/${env}/${tf_init_output}"

            echo "Init complete. Uploaded output to: s3://${ci_log_bucket}/${env}/${tf_init_output}"
            return "$tf_init_status"
        ;;
        #----------------
        "ci-plan")
            if [[ "$RUNNING_IN_CI" != 1 ]]; then
                echo "Command should only be used by CI pipeline" >&2
                return 1
            fi

            echo "Creating plan for aws workspace: ${env}"

            local tf_plan_output="${env}-tf-plan-output_${current_timestamp}.txt"

            cd "$terraform_dir" || return 1
            _terraform_plan "$env" "$var_file" "$plan_file" "$aws_account_id" |& tee "./${tf_plan_output}" > /dev/null
            local tf_plan_status="${PIPESTATUS[0]}"
            aws s3 cp "./${tf_plan_output}" "s3://${ci_log_bucket}/${env}/${tf_plan_output}"

            echo "Plan complete. Uploaded output output to: s3://${ci_log_bucket}/${env}/${tf_plan_output}"
            return "$tf_plan_status"
        ;;
        #----------------
        "ci-apply")

            if [[ "$RUNNING_IN_CI" != 1 ]]; then
                echo "Command should only be used by CI pipeline" >&2
                return 1
            fi

            echo "Applying change to aws workspace: ${env}"

            local tf_apply_output="${env}-tf-apply-output_${current_timestamp}.txt"

            cd "$terraform_dir" || return 1
            _terraform_apply "$env" "$plan_file" |& tee "./${tf_apply_output}" > /dev/null
            local tf_apply_status="${PIPESTATUS[0]}"
            aws s3 cp "./${tf_apply_output}" "s3://${ci_log_bucket}/${env}/${tf_apply_output}"

            echo "Apply complete. Uploaded output output to: s3://${ci_log_bucket}/${env}/${tf_apply_output}"
            return "$tf_apply_status"
        ;;
        #----------------
        "ci-destroy")
            if [[ "$RUNNING_IN_CI" != 1 ]]; then
                echo "Command should only be used by CI pipeline" >&2
                return 1
            fi

            echo "Destroying aws workspace: ${env}"

            local tf_destroy_output="${env}-tf-destroy-output_${current_timestamp}.txt"

            cd "$terraform_dir" || return 1
            _terraform_destroy "$env" "$var_file" "$aws_account_id" "-auto-approve" |& tee "./${tf_destroy_output}" > /dev/null
            local tf_destroy_status="${PIPESTATUS[0]}"
            aws s3 cp "./${tf_destroy_output}" "s3://${ci_log_bucket}/${env}/${tf_destroy_output}"

            echo "Destroy complete. Uploaded output output to: s3://${ci_log_bucket}/${env}/${tf_destroy_output}"
            return "$tf_destroy_status"
        ;;
        #----------------
    esac
}

_terraform_ci $@
