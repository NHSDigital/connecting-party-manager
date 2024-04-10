APIGEE_BASE_URL = "api.service.nhs.uk"

"""Mapping of CPM AWS Environment -> Apigee URL Suffix"""
APIGEE_URL_PREFIX_BY_ENVIRONMENT = {
    "dev": "internal-dev",
    "dev-sandbox": "internal-dev-sandbox",
    "qa": "internal-qa",
    "qa-sandbox": "internal-qa-sandbox",
    "ref": "ref",
    "int": "int",
    "int-sandbox": "sandbox",
    "prod": "",
}
