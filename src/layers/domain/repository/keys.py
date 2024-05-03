from enum import StrEnum
from typing import Generator

KEY_SEPARATOR = "#"


class TableKeys(StrEnum):
    DEVICE = "D"
    DEVICE_KEY = "DK"
    DEVICE_TYPE = "DT"
    DEVICE_KEY_TYPE = "DKT"
    DEVICE_INDEX = "DI"
    PRODUCT_TEAM = "PT"
    QUESTIONNAIRE = "Q"
    QUESTIONNAIRE_RESPONSE = "QR"

    def key(self, *args) -> str:
        return KEY_SEPARATOR.join(map(str, (self, *args)))

    def filter(
        self, iterable: list[dict[str, str]], key: str
    ) -> Generator[dict[str, str], None, None]:
        return (
            item for item in iterable if item[key].startswith(f"{self}{KEY_SEPARATOR}")
        )

    def filter_and_group(
        self, iterable: list[dict[str, str]], key: str
    ) -> Generator[tuple[str, dict[str, str]], None, None]:
        return group_by_key(
            iterable=self.filter(iterable=iterable, key=key),
            key=key,
        )


def group_by_key(
    iterable: list[dict[str, str]], key: str
) -> Generator[tuple[str, dict[str, str]], None, None]:
    """
    Groups data by the stripped key, and removes keys from the data, e.g. for key = "pk":

        >> iterable = [{"pk": "A#123", "sk": "B#345", "other_data": "567"}]
        >> group_by_key(iterable, key="pk")
        << [("123", {"other_data": "567"})]
    """
    return ((strip_key_prefix(item[key]), remove_keys(**item)) for item in iterable)


def strip_key_prefix(key: str):
    _, tail = key.split(KEY_SEPARATOR, 1)
    return tail


def remove_keys(
    pk=None,
    sk=None,
    pk_1=None,
    sk_1=None,
    pk_2=None,
    sk_2=None,
    pk_3=None,
    sk_3=None,
    pk_4=None,
    sk_4=None,
    pk_5=None,
    sk_5=None,
    **values,
):
    return values
