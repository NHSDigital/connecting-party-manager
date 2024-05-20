import re
from io import BytesIO
from types import FunctionType
from typing import IO, TYPE_CHECKING, Callable, Generator

from etl_utils.ldif.model import DistinguishedName
from smart_open import open as _smart_open

from ._ldif import LDIFParser, LDIFWriter

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


EMPTY_BYTESTRING = b""

PARSED_RECORD = tuple[DistinguishedName, dict[str, set[str]]]


def _decode_record(record: dict[str, list[bytes]]) -> dict[str, set[str]]:
    decoded_record = {}
    for field_name, field_items in record.items():
        non_empty_items = filter(bool, field_items)
        if field_name != "modifications":
            decoded_items = set(map(bytes.decode, non_empty_items))
            if decoded_items:
                decoded_record[field_name.lower()] = decoded_items
        else:
            decoded_record[field_name.lower()] = list(non_empty_items)
    return decoded_record


def parse_ldif(
    file_opener: Callable[[str | bytes], IO], path_or_data: str | bytes
) -> Generator[PARSED_RECORD, None, None]:
    with file_opener(path_or_data) as input_file:
        ldif_parser = LDIFParser(input_file=input_file)
        for raw_distinguished_name, record in ldif_parser.parse():
            distinguished_name = DistinguishedName.parse(raw_distinguished_name)
            decoded_record = _decode_record(record=record)
            yield (distinguished_name, decoded_record)


def _encode_record(record: dict[str, set[str]]) -> dict[str, list[bytes]]:
    return {
        field_name: (
            sorted(item.encode() for item in field_items)
            if field_name != "modifications"
            else field_items
        )
        for field_name, field_items in record.items()
    }


def ldif_dump(fp: IO, obj: list[PARSED_RECORD]) -> str:
    ldif_writer = LDIFWriter(output_file=fp)
    for distinguished_name, record in obj:
        ldif_writer.unparse(
            dn=distinguished_name.raw,
            record=_encode_record(record=record),
        )


class StreamBlock:
    def __init__(self, filter_terms: list[tuple[str, str]]):
        self.data = BytesIO()
        self.filters: list[FunctionType] = [
            re.compile(rf"(?i)^({key}): ({value})\n$".encode()).match
            for key, value in filter_terms
        ]
        self.reset()

    def flush(self) -> str:
        self.data.write(self.buffer)
        self.reset()

    def reset(self) -> str:
        self.buffer = bytes()
        self.keep = False

    def parse(self, line: bytes):
        if not self.keep:
            if any(filter(line) for filter in self.filters):
                self.keep = True
        self.buffer += line

    def __bool__(self):
        return bool(self.buffer) and self.keep


def filter_ldif_from_s3_by_property(
    s3_path, filter_terms: list[tuple[str, str]], s3_client: "S3Client"
) -> memoryview:
    """
    Efficiently streams a file from S3 directly into a bytes memoryview,
    filtering out any LDIF record without any (attribute_name, attribute_value)
    matching at least one of the filter terms.

    The output of this function can then be parsed using'
    'parse_ldif(file_opener=BytesIO, path_or_data=filtered_ldif)'
    """

    stream_block = StreamBlock(filter_terms)

    with _smart_open(s3_path, mode="rb", transport_params={"client": s3_client}) as f:
        for line in f.readlines():
            line_is_empty = line.strip() == EMPTY_BYTESTRING
            if line_is_empty and stream_block:
                stream_block.flush()
            elif line_is_empty:
                stream_block.reset()
            stream_block.parse(line=line)

    if stream_block:
        stream_block.flush()
    return stream_block.data.getbuffer()
