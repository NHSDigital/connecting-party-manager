import re
from ast import FunctionType

ENDPOINT_LAMBDA_MAPPING = dict[str, dict[str, FunctionType]]


class EndpointConfigurationError(Exception):
    pass


def get_endpoint_lambda_mapping() -> ENDPOINT_LAMBDA_MAPPING:
    """
    Register new API lambdas/endpoints here to enable local feature tests.

    The pattern (e.g. Organization/{id}?field={value}) indicates how to parse a given endpoint event
    in order to mock that AWS API event accordingly. For example, 'Organization/{id}?field={value}'
    would yield:

        path             = 'Organization'
        path_parameters  = {'id': something}
        query_parameters = {'value': something}
    """

    import api.createCpmProduct.index
    import api.createDevice.index
    import api.createProductTeam.index
    import api.readDevice.index
    import api.readProductTeam.index
    import api.searchDevice.index
    import api.status.index

    return {
        "POST": {
            "Device": api.createDevice.index,
            "ProductTeam": api.createProductTeam.index,
            "ProductTeam/{id}/Product": api.createCpmProduct.index,
        },
        "GET": {
            "Device/{id}": api.readDevice.index,
            "Device?device_type={device_type}": api.searchDevice.index,
            "Device?device_type={device_type}&foo={foo}": api.searchDevice.index,
            "Device?foo={foo}": api.searchDevice.index,
            "ProductTeam/{id}": api.readProductTeam.index,
            "_status": api.status.index,
        },
    }


def _template_to_regex(template: str) -> str:
    """Convert a pattern like 'Device/{id}' to a regex pattern like 'Device/(?P<id>[^\\/]+)'"""
    return re.sub(r"\{([^}]*)\}", r"(?P<\1>[^\/]+)", template)


def _parse_params_from_url(
    path_template: str, path: str
) -> tuple[dict[str, str], dict[str, str], bool]:
    """
    Parses path and query parameters from a URL. The return value
    is expected to be 'path_params, query_params, result' where
    path_params and query_params may be empty, and result is True
    if the provided path_template is a valid regex against the provided
    path.

    For example:
        path_template    = Organization/{id}?field={value}
        path             = Organization/123?field=456
    would yield:
        path_parameters  = {'id': 123}
        query_parameters = {'value': 456}
        result           = True

    however
        path_template    = Organization/{id}?field={value}
        path             = Organization/123
    would yield:
        path_parameters  = {'id': 123}
        query_parameters = {}
        result           = False      <-- query params failed match
    """
    # Split path from query
    path_template, *_query_template = path_template.split("?")
    path, *_query = path.split("?")
    result = True

    # Parse query against template
    query_match = None
    if _query_template and _query:
        (query,) = _query
        (query_template,) = _query_template
        query_pattern = _template_to_regex(query_template)
        query_match = re.match(query_pattern, query)
        result = query_match is not None
    query_params = query_match.groupdict() if query_match else {}

    # Parse path against template
    path_pattern = _template_to_regex(path_template)
    path_match = re.match(path_pattern, path)
    path_params = path_match.groupdict() if path_match else {}

    result = result & bool(path_match)
    return path_params, query_params, result


def parse_api_path(
    method: str, path: str, endpoint_lambda_mapping: ENDPOINT_LAMBDA_MAPPING
):
    """
    Iterate over 'endpoint_lambda_mapping' to find a matching method/path/index
    and parse out any path and query parameters
    """
    path_index_mapping = endpoint_lambda_mapping.get(method, {})
    for path_template, index in path_index_mapping.items():
        path_params, query_params, result = _parse_params_from_url(
            path_template=path_template, path=path
        )
        if result:
            return (path_params, query_params, index)
    raise EndpointConfigurationError(
        "Configuration error: add the index for"
        f" ({method}, {path}) to endpoint_lambda_mapping"
    )
