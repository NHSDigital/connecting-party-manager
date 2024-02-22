from urllib.parse import urlparse


def url(value):
    parsed_url = urlparse(value)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError("Invalid URL format")


def empty_str(value):
<<<<<<< HEAD
    if isinstance(value, str) and len(value) != 0:
        raise ValueError("Expected empty string")
=======
    if type(value) == str:
        if not len(value) == 0:
            raise ValueError("Expected empty string")
>>>>>>> dabc929 (Added multiple answer types functionality and empty string custom rule)
