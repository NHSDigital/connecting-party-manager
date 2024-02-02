from urllib.parse import urlparse


def url(value):
    parsed_url = urlparse(value)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError("Invalid URL format")
