set -e

# Parse the FHIR objects and interactions
ARGS=$(poetry run python -c "import yaml, sys; print(\";\".join(f\"{k}({','.join(v)})\" for k, v in yaml.safe_load(open(\"${PATH_TO_FHIR_DEFINITIONS}\")).items()))")

ls -l ${PATH_TO_SWAGGER_GENERATOR_JAR}

# Generate the swagger
java -jar ${PATH_TO_SWAGGER_GENERATOR_JAR} "${ARGS}" &> /dev/null

# Remove the generic definitions we don't need
rm openapi/all-openapi.json
rm openapi/batch-openapi.json
rm openapi/metadata-openapi.json

# Copy the remaining ones we do need
rm ${SWAGGER_FHIR_BASE}/*json &> /dev/null || :
mv openapi/*json ${SWAGGER_FHIR_BASE}

# Clean up
rmdir openapi
