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
        "  -- Error 1 --\n"
        "  oops\n"
        "  -- Error 2 --\n"
        "  inner-group\n"
        "    -- Error 2.1 --\n"
        "    inner-inner-group\n"
        "      -- Error 2.1.1 --\n"
        "      inner-inner-oops\n"
        "    -- Error 2.2 --\n"
        "    inner-oops-note-1, inner-oops-note-2\n"
        "    inner-oops"
    )
