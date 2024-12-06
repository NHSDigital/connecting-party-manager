from etl.sds.worker.load_bulk_reduce.load_bulk_reduce import (
    combine_error_messages,
    handler,
)


def test_combine_error_messages():
    assert (
        combine_error_messages("foo", None, None, "bar", None)
        == "foo\n--- NEXT ERROR ---\nbar"
    )


def test_combine_error_messages_all_None():
    assert combine_error_messages(None, None, None) is None


def test_bulk_load_reduce_handler_empty():
    assert handler(event=[], context=None) == {
        "stage_name": "load",
        "processed_records": 0,
        "unprocessed_records": 0,
        "error_message": None,
    }


def test_bulk_load_reduce_handler_combined():
    assert handler(
        event=[
            {
                "stage_name": "foo",
                "processed_records": 12,
                "unprocessed_records": 3,
                "error_message": "foo",
            },
            {
                "stage_name": "bar",
                "processed_records": 2,
                "unprocessed_records": 1,
                "error_message": "bar",
            },
            {
                "stage_name": "bar",
                "processed_records": 13,
                "unprocessed_records": 5,
                "error_message": None,
            },
        ],
        context=None,
    ) == {
        "stage_name": "load",
        "processed_records": 27,
        "unprocessed_records": 9,
        "error_message": "foo\n--- NEXT ERROR ---\nbar",
    }
