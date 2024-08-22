import pytest
from domain.repository.marshall import marshall, marshall_value, unmarshall_value


class Nested:
    def __init__(self, depth=0):
        if depth > 0:
            self.child = Nested(depth - 1)
        self.depth = depth


@pytest.mark.parametrize(
    "value,expected",
    [
        [None, {"NULL": True}],
        ["foo", {"S": "foo"}],
        [123, {"N": "123"}],
        [True, {"BOOL": True}],
        [[], {"L": []}],
        [set(), {"L": []}],
        [
            [
                None,
                1,
                2.0,
                "3",
                False,
                [],
                {},
            ],
            {
                "L": [
                    {"NULL": True},
                    {"N": "1"},
                    {"N": "2.0"},
                    {"S": "3"},
                    {"BOOL": False},
                    {"L": []},
                    {"M": {}},
                ]
            },
        ],
        [
            {
                "none": None,
                "bool": False,
                "int": 1,
                "float": 2,
                "string": "str",
                "list": [],
                "map": {},
            },
            {
                "M": {
                    "none": {"NULL": True},
                    "bool": {"BOOL": False},
                    "int": {"N": "1"},
                    "float": {"N": "2"},
                    "string": {"S": "str"},
                    "list": {"L": []},
                    "map": {"M": {}},
                }
            },
        ],
    ],
)
def test_marshall_value(value, expected):
    actual = marshall_value(value)
    assert actual == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        [{"NULL": True}, None],
        [{"BOOL": False}, False],
        [{"BOOL": True}, True],
        [{"N": "0"}, 0.0],
        [{"N": "1"}, 1.0],
        [{"N": "1.2"}, 1.2],
        [{"S": "x"}, "x"],
        [{"L": []}, []],
        [{"L": [{"NULL": True}]}, [None]],
        [{"M": {}}, {}],
        [{"M": {"foo": {"BOOL": False}, "bar": {"N": "1"}}}, {"foo": False, "bar": 1}],
    ],
)
def test__unmarshall_value(value, expected):
    actual = unmarshall_value(value)
    assert actual == expected


def test_marshall():
    input = {"one": 1, "two": 2, "three": 3}
    actual = marshall(pk="_pk_", pk_1="_pk_1_", sk_5="_sk_5_", **input)
    expected = {
        "pk": {"S": "_pk_"},
        "pk_1": {"S": "_pk_1_"},
        "sk_5": {"S": "_sk_5_"},
        "one": {"N": "1"},
        "two": {"N": "2"},
        "three": {"N": "3"},
    }
    assert actual == expected
