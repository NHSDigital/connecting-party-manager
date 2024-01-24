import re
from typing import Self

from pydantic import BaseModel


class BadDistinguishedName(Exception):
    pass


DISTINGUISHED_NAME_RE = re.compile(r"([^,]+)=([^,]+)")


class DistinguishedName(BaseModel):
    parts: tuple[tuple[str, str], ...]

    @classmethod
    def parse(cls, raw_distinguished_name: str) -> Self:
        unsorted_parts = DISTINGUISHED_NAME_RE.findall(raw_distinguished_name)
        if not unsorted_parts:
            raise BadDistinguishedName(raw_distinguished_name)
        sorted_parts = sorted(unsorted_parts, key=lambda *args: args)
        return cls(parts=tuple(sorted_parts))

    def __eq__(self, other: "DistinguishedName"):
        return self.parts == other.parts

    def __hash__(self):
        return hash(self.parts)
