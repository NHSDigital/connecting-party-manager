class DuplicateError(Exception):
    pass


class NotFoundError(Exception):
    pass


class InvalidOdsCodeError(Exception):
    pass


class BadProductIdError(Exception):
    pass


class BadAsidError(Exception):
    pass


class BadProductIdOrAsidError(ExceptionGroup):
    EXCEPTION_GROUP = (BadProductIdError, BadAsidError)

    def __new__(cls, id: str):
        """
        This is the recommended pattern for deriving from ExceptionGroup,
        see https://docs.python.org/3/library/exceptions.html
        """
        self = super().__new__(
            BadProductIdOrAsidError,
            f"Product ID or ASID required: {id}",
            BadProductIdOrAsidError.EXCEPTION_GROUP,
        )
        return self


class BadUuidError(Exception):
    pass


class BadEntityNameError(Exception):
    pass


class InvalidTypeError(Exception):
    pass
