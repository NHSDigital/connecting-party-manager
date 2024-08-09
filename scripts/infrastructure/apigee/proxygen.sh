set -e

PATH_TO_HERE="scripts/infrastructure/apigee"
APIGEE_DEPLOYMENT_ROLE="NHSDeploymentRole"

if [[ -z ${WORKSPACE_OUTPUT_JSON} ]]; then
    echo "WORKSPACE_OUTPUT_JSON not set"
    exit 1
fi

if [[ -z ${ENVIRONMENT_MAPPING_YAML} ]]; then
    echo "ENVIRONMENT_MAPPING_YAML not set"
    exit 1
fi

if [[ -z ${STAGE_MAPPING_YAML} ]]; then
    echo "STAGE_MAPPING_YAML not set"
    exit 1
fi

if [[ -z ${APIGEE_CONFIG_PATH} ]]; then
    echo "APIGEE_CONFIG_PATH not set"
    exit 1
fi

if [[ -z ${SWAGGER_APIGEE} ]]; then
    echo "SWAGGER_APIGEE not set"
    exit 1
fi

function get_workspace_name(){
    jq -r '.workspace.value' ${WORKSPACE_OUTPUT_JSON}
}

function get_aws_environment(){
    jq -r '.environment.value' ${WORKSPACE_OUTPUT_JSON}
}

function get_apigee_environment(){
    workspace_name=${1}
    aws_environment=${2}

    _scoped_environment=${aws_environment}
    if [[ ${workspace_name} == "${aws_environment}-sandbox" ]]; then
        _scoped_environment=${workspace_name}
    fi

    apigee_environment=$(yq ".${_scoped_environment}" ${ENVIRONMENT_MAPPING_YAML})
    if [[ ${apigee_environment} == "null" ]]; then
        # Default to internal-dev if not named in ${ENVIRONMENT_MAPPING_YAML}
        echo "internal-dev"
    else
        echo ${apigee_environment}
    fi
}

function get_apigee_stage(){
    workspace_name=${1}
    apigee_stage=$(yq ".${workspace_name}" ${STAGE_MAPPING_YAML})
    if [[ ${apigee_stage} == "null" ]]; then
        # Default to ptl if not named in ${STAGE_MAPPING_YAML}
        echo "ptl"
    else
        echo ${apigee_stage}
    fi
}

function generate_proxy(){
    _workspace_name=$(get_workspace_name)
    _aws_environment=$(get_aws_environment)
    _apigee_environment=$(get_apigee_environment ${_workspace_name} ${_aws_environment})
    _apigee_stage=$(get_apigee_stage ${_workspace_name})

        echo "
    Apigeeing
    -------------------- ----------------------------------------
    workspace_name        ${_workspace_name}
    aws_environment       ${_aws_environment}
    apigee_environment    ${_apigee_environment}
    apigee_stage          ${_apigee_stage}
"

    # Some validation rules to avoid being rejected by proxygen:
    # 1. No double hyphens part 1
    if [[ ${_workspace_name} == *--* ]];
    then
        echo "proxy name must not contain '--'"
        exit 1
    fi

    # 2. Since we will prefix with 'connecting-party-manager-'
    # we cannot start with a hyphen either
    if [[ ${_workspace_name} == -* ]];
    then
        echo "proxy name must start with '-'"
        exit 1
    fi

    #3. Apigee services expect int-sandbox to be sandbox to match
    if [[ ${_workspace_name} == "int-sandbox" ]];
    then
        _workspace_name="sandbox"
    fi

    # Download the pem file if it does not exist
    if [ ! -f "${APIGEE_CONFIG_PATH}/${_apigee_stage}/.proxygen/private_key.pem" ]; then
        poetry run python ${PATH_TO_HERE}/download_pem.py ${_apigee_stage} ${APIGEE_DEPLOYMENT_ROLE}
    fi

    DOT_PROXYGEN=${APIGEE_CONFIG_PATH}/${_apigee_stage} \
        poetry run \
        python ${PATH_TO_HERE}/proxygen.py instance deploy \
        ${_apigee_environment} \
        cpm-${_workspace_name} \
        ${SWAGGER_APIGEE} \
        --no-confirm
}

function delete_proxy(){
    _workspace_name=$(get_workspace_name)
    _aws_environment=$(get_aws_environment)
    _apigee_environment=$(get_apigee_environment ${_workspace_name} ${_aws_environment})
    _apigee_stage=$(get_apigee_stage ${_workspace_name})

        echo "
    Deleting proxy
    -------------------- ----------------------------------------
    workspace_name        ${_workspace_name}
    aws_environment       ${_aws_environment}
    apigee_environment    ${_apigee_environment}
    apigee_stage          ${_apigee_stage}
"

    # Some validation rules to avoid being rejected by proxygen:
    # 1. No double hyphens part 1
    if [[ ${_workspace_name} == *--* ]];
    then
        echo "proxy name must not contain '--'"
        exit 1
    fi

    # 2. Since we will prefix with 'connecting-party-manager-'
    # we cannot start with a hyphen either
    if [[ ${_workspace_name} == -* ]];
    then
        echo "proxy name must start with '-'"
        exit 1
    fi

    #3. Apigee services expect int-sandbox to be sandbox to match
    if [[ ${_workspace_name} == "int-sandbox" ]];
    then
        _workspace_name="sandbox"
    fi

    # Download the pem file if it does not exist
    if [ ! -f "${APIGEE_CONFIG_PATH}/${_apigee_stage}/.proxygen/private_key.pem" ]; then
        poetry run python ${PATH_TO_HERE}/download_pem.py ${_apigee_stage} ${APIGEE_DEPLOYMENT_ROLE}
    fi

    DOT_PROXYGEN=${APIGEE_CONFIG_PATH}/${_apigee_stage} \
        poetry run \
        python ${PATH_TO_HERE}/proxygen.py instance delete \
        ${_apigee_environment} \
        cpm-${_workspace_name} \
        --no-confirm
}

# Expose functions publicly
$@
