import re

ACCREDITED_SYSTEM_ID = r"^[0-9]{1,12}$"


class InvalidAccreditedSystemIdError(Exception):
    pass


class AccreditedSystemId(str):
    """
    Accredited System Id (ASID) is a 12 digit positive number 1-999,999,999,999.
    Within the CPM it is being stored as a string, in order to standardise it
    with all of the other identifiers, which are expressed as strings.
    """

    def __new__(cls, content):
        if not re.match(ACCREDITED_SYSTEM_ID, content):
            raise InvalidAccreditedSystemIdError(
                f"Invalid Accredited System Id: {content}"
            )
        return str.__new__(cls, content)
