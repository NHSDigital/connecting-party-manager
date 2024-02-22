from urllib.parse import urlparse


def url(value):
    parsed_url = urlparse(value)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError("Invalid URL format")


def empty_str(value):
    if isinstance(value, str):
        if len(value) != 0:
            raise ValueError("Expected empty string")
