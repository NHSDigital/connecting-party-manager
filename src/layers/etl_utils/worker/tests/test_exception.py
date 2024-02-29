from etl_utils.worker.exception import render_exception


def test__render_exception_group():
    inner_oops = ValueError("inner-oops")
    inner_oops.add_note("inner-oops-note-1")
    inner_oops.add_note("inner-oops-note-2")

    nested_exception = ExceptionGroup(
        "outer-group",
        [
            ValueError("oops"),
            ExceptionGroup(
                "inner-group",
                [
                    ExceptionGroup(
                        "inner-inner-group",
                        [
                            ValueError("inner-inner-oops"),
                        ],
                    ),
                    inner_oops,
                ],
            ),
        ],
    )
    assert render_exception(nested_exception) == (
        "outer-group\n"
        "  -- Error 1 (ValueError) --\n"
        "  oops\n"
        "  -- Error 2 (ExceptionGroup) --\n"
        "  inner-group\n"
        "    -- Error 2.1 (ExceptionGroup) --\n"
        "    inner-inner-group\n"
        "      -- Error 2.1.1 (ValueError) --\n"
        "      inner-inner-oops\n"
        "    -- Error 2.2 (ValueError) --\n"
        "    inner-oops-note-1, inner-oops-note-2\n"
        "    inner-oops"
    )
