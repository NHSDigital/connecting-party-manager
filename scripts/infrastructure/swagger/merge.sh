set -e

PATH_TO_SWAGGER_INFRA=${PWD}/infrastructure/swagger
PATH_TO_SWAGGER_DIST=${PATH_TO_SWAGGER_INFRA}/dist
PATH_TO_SWAGGER_BUILD=${PATH_TO_SWAGGER_DIST}/build
PATH_TO_SWAGGER_AWS=${PATH_TO_SWAGGER_DIST}/aws
PATH_TO_SWAGGER_PUBLIC=${PATH_TO_SWAGGER_DIST}/public

mkdir -p ${PATH_TO_SWAGGER_AWS}
mkdir -p ${PATH_TO_SWAGGER_PUBLIC}
mkdir -p ${PATH_TO_SWAGGER_BUILD}

AWS_SWAGGER_FILE=${PATH_TO_SWAGGER_AWS}/swagger.yaml
PUBLIC_SWAGGER_FILE=${PATH_TO_SWAGGER_PUBLIC}/swagger.yaml
_BASE_SWAGGER_FILE=${PATH_TO_SWAGGER_INFRA}/00_base.yaml
_INITIAL_MERGE_SWAGGER_FILE=${PATH_TO_SWAGGER_BUILD}/_01_initial_merge.yaml
_CLEANED_SWAGGER_FILE=${PATH_TO_SWAGGER_BUILD}/_02_clean.yaml

swagger_files=$(find ${PATH_TO_SWAGGER_INFRA}/*yaml | sort -g)

yq eval-all '. as $item ireduce ({}; . * $item)' ${_BASE_SWAGGER_FILE} ${swagger_files} > ${_INITIAL_MERGE_SWAGGER_FILE}

cat ${_INITIAL_MERGE_SWAGGER_FILE} |
    # Remove commented lines
    grep -v "^\s*#" |
    # Replace snake case terms, which are invalid in ApiGateway
    yq 'with(.components.schemas; with_entries(.key |= sub("_","")))' |
    yq '(.. | select(has("$ref")).$ref) |= sub("_","")' |
    # Remove autogenerated parts that we don't want
    yq 'del(.paths.*.post.requestBody.content."application/x-www-form-urlencoded")' |
    yq 'del(.x-ibm-configuration)' |
    yq 'del(.components.schemas.*.discriminator)' |
    yq '(.. | select(style == "single")) style |= "double"' \
        > ${_CLEANED_SWAGGER_FILE}


# Remove fields not required for public docs
# * AWS specific stuff, including security & lambdas
# * security tags
# * API catalogue dislikes tags
# * /_status not public
cat ${_CLEANED_SWAGGER_FILE} |
    yq 'with(.paths.*.*.responses.*.content; with_entries(.key |= . + ";version=1" ))' |
    yq 'with(.components.requestBodies.*.content; with_entries(.key |= . + ";version=1" ))' |
    yq 'with(.components.responses.*.content; with_entries(.key |= . + ";version=1" ))' |
    yq 'del(.paths.*.*.x-amazon-apigateway-integration)' |
    yq 'del(.x-*)' |
    yq 'del(.paths.*.*.security)' |
    yq 'del(.tags)' |
    yq 'del(.paths.*.*.tags)' |
    yq 'del(.paths./_status)' |
    yq 'del(.components.securitySchemes."${authoriser_name}")' \
        > ${PUBLIC_SWAGGER_FILE}


# Remove fields not valid on AWS but otherwise required in public docs
# * 4XX codes
# * Expand anchors and remove corresponding x-definitions
cat ${_CLEANED_SWAGGER_FILE} |
    yq 'del(.. | select(has("4XX")).4XX)' |
    yq 'explode(.)' |
    yq 'del(.x-*)' > ${AWS_SWAGGER_FILE}

rm -r ${PATH_TO_SWAGGER_BUILD}