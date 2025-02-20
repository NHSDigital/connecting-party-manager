from dataclasses import asdict

from etl_utils.worker.model import WorkerResponse


def combine_error_messages(*args) -> str | None:
    non_null_error_messages = filter(lambda x: isinstance(x, str), args)
    combined_error_message = "\n--- NEXT ERROR ---\n".join(non_null_error_messages)
    return combined_error_message or None


def handler(event: list[dict], context):
    combined_response = WorkerResponse(stage_name="load")
    for _response in event:
        response = WorkerResponse(**_response)
        combined_response.processed_records += response.processed_records
        combined_response.unprocessed_records += response.unprocessed_records
        combined_response.error_message = combine_error_messages(
            combined_response.error_message, response.error_message
        )
    return asdict(combined_response)
