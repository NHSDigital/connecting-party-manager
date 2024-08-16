import pytest
from domain.core.compression import pkl_dumps_gzip, pkl_loads_gzip


class MyThing:
    a = "123"

    def __eq__(self, other: "MyThing"):
        return self.a == other.a


@pytest.mark.parametrize(
    "obj",
    [
        "a string",
        MyThing(),
        12332,
        {
            "a key": "a value",
            "another key": {
                "a nested key": ["a nested list"],
            },
        },
    ],
)
def test_compression(obj):
    compressed = pkl_dumps_gzip(obj)
    assert pkl_loads_gzip(compressed) == obj
