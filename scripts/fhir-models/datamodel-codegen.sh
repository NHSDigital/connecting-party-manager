set -e
poetry run datamodel-codegen \
    --input ${SWAGGER_AWS} \
    --input-file-type openapi \
    --output ${MODEL_PATH} \
    --use-annotated \
    --enum-field-as-literal all \
    --use-double-quotes ${EXTRA_CODEGEN_ARGS}
echo "Generated ${MODEL_PATH} from ${SWAGGER_AWS}"
