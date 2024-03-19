from collections import deque
from types import FunctionType


def apply_action(
    unprocessed_records: deque,
    processed_records: deque,
    action: FunctionType,
    record_serializer=None,
    max_records: int = None,
):
    index = 0
    exception = None

    while (
        unprocessed_records
        and exception is None
        and (max_records is None or index < max_records)
    ):
        record = unprocessed_records[0]
        try:
            response = action(record=record)
        except Exception as _exception:
            if record_serializer is not None:
                record = record_serializer(record)
            _exception.add_note(f"Failed to parse record {index}\n{record}")
            exception = _exception
        else:
            if isinstance(response, (list, deque)):
                processed_records += response
            else:
                processed_records.append(response)
            unprocessed_records.popleft()
            index += 1
    return exception
