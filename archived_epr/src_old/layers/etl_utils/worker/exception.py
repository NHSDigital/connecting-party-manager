"""
Unfortunately as of Python 3.11, ExceptionGroup does not fully support
string rendering (i.e. 'str(exception_group)' is not very useful) so here
we have implemented 'render_exception' which fully and recursively
stringifies an ExceptionGroup in the form:

>    outer-group
>      -- Error 1 (ValueError) --
>      oops
>      -- Error 2 (ExceptionGroup) --
>      inner-group
>        -- Error 2.1 (ExceptionGroup) --
>        inner-inner-group
>          -- Error 2.1.1 (TypeError) --
>          inner-inner-oops
>        -- Error 2.2 (ValueError) --
>        inner-oops-note-1, inner-oops-note-2
>        inner-oops
"""

from traceback import TracebackException

INDENTATION = "  "
TRUNCATION_DEPTH = 2000
TRUNCATED = "[TRUNCATED]\n"


def truncate_message(
    item: str, truncation_depth=TRUNCATION_DEPTH, truncated_note=TRUNCATED
):
    if len(item) > truncation_depth:
        return item[:truncation_depth] + truncated_note
    return item


def _render_exception(exception: Exception) -> str:
    """Concatenates an exception with its notes"""
    _notes = exception.__dict__.get("__notes__", [])
    notes = ", ".join(_notes) + "\n" if _notes else ""
    return f"{notes}{exception}"


def _render_nested_exception(
    exception: Exception, nested_index: list[int], truncation_depth: int
):
    """
    Renders an exception that is part of a group, noting that the
    exception itself may also be a group.

    NB: nested_index refers to the error index
    (e.g. 2.2.1 is provided in the form [2,2,1])
    """
    indentation = INDENTATION * len(nested_index)
    message = render_exception(
        exception=exception,
        nested_index=nested_index,
        truncation_depth=truncation_depth,
    )
    error_index = ".".join(map(str, nested_index))
    prefix = f"-- Error {error_index} ({type(exception).__name__}) --\n"

    return f"{indentation}{prefix}{message}"


def _render_exception_group(
    exception_group: ExceptionGroup,
    truncation_depth: int,
    nested_index: list[int] = None,
) -> str:
    """Concatenates an exception group message to its rendered exceptions"""
    formatted_exceptions = "\n".join(
        _render_nested_exception(
            exception=exception,
            nested_index=(nested_index + [i]) if nested_index else [i],
            truncation_depth=truncation_depth,
        )
        for i, exception in enumerate(exception_group.exceptions, start=1)
    )
    return f"{exception_group.message}\n{formatted_exceptions}"


def render_exception(
    exception: ExceptionGroup | Exception,
    nested_index=None,
    truncation_depth=TRUNCATION_DEPTH,
) -> str:
    """Fully and recursively stringifies an Exception or ExceptionGroup"""

    nested_index = nested_index if nested_index else []
    indentation = INDENTATION * len(nested_index)
    formatted_exception = (
        _render_exception_group(
            exception_group=exception,
            nested_index=nested_index,
            truncation_depth=truncation_depth,
        )
        if isinstance(exception, ExceptionGroup)
        else _render_exception(exception=exception).replace("\n", f"\n{indentation}")
    )

    _traceback = "".join(TracebackException.from_exception(exception).format())
    if truncation_depth is not None and len(formatted_exception) > truncation_depth:
        formatted_exception = truncate_message(
            formatted_exception, truncation_depth=truncation_depth
        )

    if truncation_depth is not None and len(_traceback) > truncation_depth:
        _traceback = truncate_message(_traceback, truncation_depth=truncation_depth)

    return f"{indentation}{formatted_exception}\n{_traceback}\n"
