class DuplicateError(Exception):
    pass


class NotFoundError(Exception):
    pass


class InvalidKeyPattern(ValueError):
    pass


class InvalidProductTeamKeyError(ValueError):
    pass


class InvalidKeyError(Exception):
    pass


class InvalidProductIdError(Exception):
    pass


class InvalidAccreditedSystemIdError(Exception):
    pass


class InvalidResponseError(ValueError):
    pass


class UnknownFields(Exception):
    pass


class ImmutableFieldError(Exception):
    pass


class EventUpdatedError(Exception):
    pass


class EventExpected(Exception):
    pass
