from domain.response.coding import SpineCoding
from domain.response.response_matrix import spine_coding_from_exception
from domain.response.validation_errors import parse_validation_error
from pydantic import BaseModel, ValidationError


class ErrorItem(BaseModel):
    code: SpineCoding
    message: str


class ErrorResponse(BaseModel):
    errors: list[ErrorItem]

    @classmethod
    def from_validation_error(cls, exception: ValidationError):
        validation_error_items = parse_validation_error(validation_error=exception)
        return cls(
            errors=[
                ErrorItem(
                    code=spine_coding_from_exception(exception=item.exception_type),
                    message=f"{item.path}: {item.msg}",
                )
                for item in validation_error_items
            ]
        )

    @classmethod
    def from_exception(cls, exception: Exception):
        error_code = spine_coding_from_exception(exception=exception)
        error_item = ErrorItem(code=error_code, message=str(exception))
        return cls(errors=[error_item])
