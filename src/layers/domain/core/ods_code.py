import re

ODS_CODE_REGEX = r"^[A-Z0-9]{1,5}$"


class InvalidOdsCodeError(Exception):
    pass


class OdsCode(str):
    def __new__(cls, content):
        if not re.match(ODS_CODE_REGEX, content):
            raise InvalidOdsCodeError(f"Invalid ODS Code: {content}")
        return str.__new__(cls, content)
