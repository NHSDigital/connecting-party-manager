from locust import HttpUser, events, task

queries = [
    {
        "params": {
            "organization": ["https://fhir.nhs.uk/Id/ods-organization-code|E82652"],
            "identifier": [
                "https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:gpconnect:fhir:operation:gpc.getcarerecord",
                "https://fhir.nhs.uk/Id/nhsMhsPartyKey|E82652-826971",
            ],
        },
        "path": "/Device",
    }
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
    @task
    def search(self):
        apikey = self.environment.parsed_options.apikey
        API_VERSION = self.environment.parsed_options.api_version
        USE_CPM = self.environment.parsed_options.usecpm
        for query in queries:
            params = query["params"].copy()
            if USE_CPM == "TRUE":
                params["use_cpm"] = "iwanttogetdatafromcpm"

            url_path = f"{query['path']}"
            self.client.get(
                url=url_path,
                params=params,
                headers=_get_headers(version=API_VERSION, apikey=apikey),
            )
