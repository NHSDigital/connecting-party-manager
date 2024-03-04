from collections import deque
from types import FunctionType


def apply_action(
    unprocessed_records: deque,
    processed_records: list,
    action: FunctionType,
    record_serializer=None,
):
    index = 0
    exception = None

    while unprocessed_records and exception is None:
        record = unprocessed_records[0]
        try:
            response = action(record=record)
        except Exception as _exception:
            if record_serializer is not None:
                record = record_serializer(record)
            _exception.add_note(f"Failed to parse record {index}\n{record}")
            exception = _exception
        else:
            if isinstance(response, list):
                processed_records += response
            else:
                processed_records.append(response)
            unprocessed_records.popleft()
            index += 1
    return exception
