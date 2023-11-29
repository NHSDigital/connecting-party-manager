from urllib.parse import quote_plus

from requests import HTTPError, Response, request


def make_request(
    base_url: str,
    http_method: str,
    endpoint: str,
    headers: dict[str, str],
    body: dict = None,
    raise_for_status=False,
) -> Response:
    url = base_url + "/".join(map(quote_plus, endpoint.split("/")))
    response = request(method=http_method, url=url, json=body, headers=headers)
    if raise_for_status:
        try:
            response.raise_for_status()
        except HTTPError:
            print(response.text)  # noqa: T201
            raise
    return response
