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
        "ValueError: oops\n"
        "\n"
        "\n"
        "  -- Error 2 (ExceptionGroup) --\n"
        "  inner-group\n"
        "    -- Error 2.1 (ExceptionGroup) --\n"
        "    inner-inner-group\n"
        "      -- Error 2.1.1 (ValueError) --\n"
        "      inner-inner-oops\n"
        "ValueError: inner-inner-oops\n"
        "\n"
        "\n"
        "  | ExceptionGroup: inner-inner-group (1 sub-exception)\n"
        "  +-+---------------- 1 ----------------\n"
        "    | ValueError: inner-inner-oops\n"
        "    +------------------------------------\n"
        "\n"
        "\n"
        "    -- Error 2.2 (ValueError) --\n"
        "    inner-oops-note-1, inner-oops-note-2\n"
        "    inner-oops\n"
        "ValueError: inner-oops\n"
        "inner-oops-note-1\n"
        "inner-oops-note-2\n"
        "\n"
        "\n"
        "  | ExceptionGroup: inner-group (2 sub-exceptions)\n"
        "  +-+---------------- 1 ----------------\n"
        "    | ExceptionGroup: inner-inner-group (1 sub-exception)\n"
        "    +-+---------------- 1 ----------------\n"
        "      | ValueError: inner-inner-oops\n"
        "      +------------------------------------\n"
        "    +---------------- 2 ----------------\n"
        "    | ValueError: inner-oops\n"
        "    | inner-oops-note-1\n"
        "    | inner-oops-note-2\n"
        "    +------------------------------------\n"
        "\n\n"
        "  | ExceptionGroup: outer-group (2 sub-exceptions)\n"
        "  +-+---------------- 1 ----------------\n"
        "    | ValueError: oops\n"
        "    +---------------- 2 ----------------\n"
        "    | ExceptionGroup: inner-group (2 sub-exceptions)\n"
        "    +-+---------------- 1 ----------------\n"
        "      | ExceptionGroup: inner-inner-group (1 sub-exception)\n"
        "      +-+---------------- 1 ----------------\n"
        "        | ValueError: inner-inner-oops\n"
        "        +------------------------------------\n"
        "      +---------------- 2 ----------------\n"
        "      | ValueError: inner-oops\n"
        "      | inner-oops-note-1\n"
        "      | inner-oops-note-2\n"
        "      +------------------------------------\n"
        "\n"
    )


def test__render_exception_group_truncation():
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

    assert render_exception(nested_exception, truncation_depth=150) == (
        "outer-group\n"
        "  -- Error 1 (ValueError) --\n"
        "  oops\n"
        "ValueError: oops\n"
        "\n"
        "\n"
        "  -- Error 2 (ExceptionGroup) --\n"
        "  inner-group\n"
        "    -- Error 2.1 (ExceptionGroup) --[TRUNCATED]\n"
        "\n"
        "  | ExceptionGroup: outer-group (2 sub-exceptions)\n"
        "  +-+---------------- 1 ----------------\n"
        "    | ValueError: oops\n"
        "    +---------------- 2 -----------[TRUNCATED]\n"
        "\n"
    )


def test__render_exception_group_null_truncation():
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
    assert render_exception(nested_exception, truncation_depth=None) == (
        "outer-group\n"
        "  -- Error 1 (ValueError) --\n"
        "  oops\n"
        "ValueError: oops\n"
        "\n"
        "\n"
        "  -- Error 2 (ExceptionGroup) --\n"
        "  inner-group\n"
        "    -- Error 2.1 (ExceptionGroup) --\n"
        "    inner-inner-group\n"
        "      -- Error 2.1.1 (ValueError) --\n"
        "      inner-inner-oops\n"
        "ValueError: inner-inner-oops\n"
        "\n"
        "\n"
        "  | ExceptionGroup: inner-inner-group (1 sub-exception)\n"
        "  +-+---------------- 1 ----------------\n"
        "    | ValueError: inner-inner-oops\n"
        "    +------------------------------------\n"
        "\n"
        "\n"
        "    -- Error 2.2 (ValueError) --\n"
        "    inner-oops-note-1, inner-oops-note-2\n"
        "    inner-oops\n"
        "ValueError: inner-oops\n"
        "inner-oops-note-1\n"
        "inner-oops-note-2\n"
        "\n"
        "\n"
        "  | ExceptionGroup: inner-group (2 sub-exceptions)\n"
        "  +-+---------------- 1 ----------------\n"
        "    | ExceptionGroup: inner-inner-group (1 sub-exception)\n"
        "    +-+---------------- 1 ----------------\n"
        "      | ValueError: inner-inner-oops\n"
        "      +------------------------------------\n"
        "    +---------------- 2 ----------------\n"
        "    | ValueError: inner-oops\n"
        "    | inner-oops-note-1\n"
        "    | inner-oops-note-2\n"
        "    +------------------------------------\n"
        "\n"
        "\n"
        "  | ExceptionGroup: outer-group (2 sub-exceptions)\n"
        "  +-+---------------- 1 ----------------\n"
        "    | ValueError: oops\n"
        "    +---------------- 2 ----------------\n"
        "    | ExceptionGroup: inner-group (2 sub-exceptions)\n"
        "    +-+---------------- 1 ----------------\n"
        "      | ExceptionGroup: inner-inner-group (1 sub-exception)\n"
        "      +-+---------------- 1 ----------------\n"
        "        | ValueError: inner-inner-oops\n"
        "        +------------------------------------\n"
        "      +---------------- 2 ----------------\n"
        "      | ValueError: inner-oops\n"
        "      | inner-oops-note-1\n"
        "      | inner-oops-note-2\n"
        "      +------------------------------------\n"
        "\n"
    )
