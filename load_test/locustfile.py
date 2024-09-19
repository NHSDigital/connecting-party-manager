import random

from locust import HttpUser, events, task
from speed_test_queries import queries


class QueryParams:
    LDAP_UNIQUE_IDENTIFIER = "ldap_unique_identifier"
    DEVICE_ID = "device_id"
    DEVICE_KEY = "device_key"
    PARTY_KEY = "party_key"
    INTERACTION_ID = "interaction_id"
    ODS_CODE = "ods_code"


unique_identifiers = ["1234567", "7654321"]

device_keys = ["D81631:200000035358"]

device_ids = ["3b9ced88-e2c2-4496-8ade-7fc3d5a8aba5"]

interaction_ids = [
    "https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:lrs:REPC_IN010000UK01"
]

party_keys = ["https://fhir.nhs.uk/Id/nhsMhsPartyKey|5NR-801831"]

ods_codes = ["https://fhir.nhs.uk/Id/ods-organization-code|5NR"]


sds_accredited_system_query_combinations = [
    {QueryParams.INTERACTION_ID, QueryParams.ODS_CODE, QueryParams.PARTY_KEY},
    {QueryParams.INTERACTION_ID, QueryParams.ODS_CODE},
]

sds_mhs_query_combinations = [
    {QueryParams.INTERACTION_ID, QueryParams.ODS_CODE, QueryParams.PARTY_KEY},
    {QueryParams.INTERACTION_ID, QueryParams.PARTY_KEY},
    {QueryParams.INTERACTION_ID, QueryParams.ODS_CODE},
    {QueryParams.PARTY_KEY, QueryParams.ODS_CODE},
]


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        "--api-version",
        type=str,
        env_var="API_VERSION",
        required=True,
        default="1",
        help="version of the api to run",
    )
    parser.add_argument(
        "--apikey",
        type=str,
        env_var="APIKEY",
        required=True,
        help="apikey for hitting desired host",
    )
    parser.add_argument(
        "--usecpm",
        choices=["TRUE", "FALSE"],
        default="FALSE",
        env_var="USE_CPM",
        required=False,
        help="use_cpm for hitting cpm",
    )


def _get_headers(version: str, apikey: str):
    headers = {"Authorization": "Bearer foo", "apikey": apikey, "version": version}

    return headers


class CPMUser(HttpUser):
    # @task
    # def read_device_by_id(self):
    #     device_id = random.choice(device_ids)
    #     url_path = f"/Device/{device_id}"
    #     APIKEY = self.environment.parsed_options.apikey
    #     API_VERSION = self.environment.parsed_options.api_version

    #     self.client.get(
    #         url=url_path, headers=_get_headers(version=API_VERSION, apikey=APIKEY)
    #     )

    @task
    def search(self):
        apikey = self.environment.parsed_options.apikey
        API_VERSION = self.environment.parsed_options.api_version
        USE_CPM = self.environment.parsed_options.usecpm
        random_queries = random.sample(queries, 100)
        for query in random_queries:
            params = query["params"]
            if USE_CPM == "TRUE":
                params["use_cpm"] = "iwanttogetdatafromcpm"
            url_path = f"{query['path']}"
            self.client.get(
                url=url_path,
                params=params,
                headers=_get_headers(version=API_VERSION, apikey=apikey),
            )

    # @task
    # def search_cpm_for_unique_identifier(self):
    #     unique_identifier = random.choice(unique_identifiers)
    #     url_path = f"/Device?{QueryParams.LDAP_UNIQUE_IDENTIFIER}={unique_identifier}"
    #     apikey = self.environment.parsed_options.apikey
    #     API_VERSION = self.environment.parsed_options.api_version

    #     self.client.get(
    #         url=url_path,
    #         headers=_get_headers(version=API_VERSION, apikey=apikey)
    #     )

    # @task
    # def search_cpm_for_accredited_system(self):
    #     selected_combination = random.choice(sds_accredited_system_query_combinations)
    #     selected_values = {}
    #     if QueryParams.INTERACTION_ID in selected_combination:
    #         selected_values['interaction'] = random.choice(interaction_ids)

    #     if QueryParams.ODS_CODE in selected_combination:
    #         selected_values['code'] = random.choice(ods_codes)

    #     if QueryParams.PARTY_KEY in selected_combination:
    #         selected_values['key'] = random.choice(party_keys)

    #     query_params = urlencode(selected_values)
    #     url_path = f"/Device?{query_params}"

    #     apikey = self.environment.parsed_options.apikey
    #     API_VERSION = self.environment.parsed_options.api_version

    #     self.client.get(
    #         url=url_path,
    #         headers=_get_headers(version=API_VERSION, apikey=apikey)
    #     )

    # @task
    # def search_cpm_for_mhs(self):
    #     selected_combination = random.choice(sds_mhs_query_combinations)
    #     selected_values = {}
    #     if QueryParams.INTERACTION_ID in selected_combination:
    #         selected_values['interaction'] = random.choice(interaction_ids)

    #     if QueryParams.ODS_CODE in selected_combination:
    #         selected_values['code'] = random.choice(ods_codes)

    #     if QueryParams.PARTY_KEY in selected_combination:
    #         selected_values['key'] = random.choice(party_keys)

    #     query_params = urlencode(selected_values)
    #     url_path = f"/Device?{query_params}"

    #     apikey = self.environment.parsed_options.apikey
    #     API_VERSION = self.environment.parsed_options.api_version

    #     self.client.get(
    #         url=url_path,
    #         headers=_get_headers(version=API_VERSION, apikey=apikey)
    #     )
