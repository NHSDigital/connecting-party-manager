import re
from base64 import b64decode
from collections import defaultdict
from io import BytesIO
from types import FunctionType
from typing import IO, TYPE_CHECKING, Callable, Generator, Protocol

from etl_utils.ldif.model import DistinguishedName
from smart_open import open as _smart_open

from ._ldif import PARSED_MODIFICATION_KEY, LDIFParser, LDIFWriter

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


EMPTY_BYTESTRING = b""

PARSED_RECORD = tuple[DistinguishedName, dict[str, set[str]]]


def _decode_record(record: dict[str, list[bytes]]) -> dict[str, set[str]]:
    decoded_record = {}
    for field_name, field_items in record.items():
        non_empty_items = filter(bool, field_items)

        # "modification" items are not arrays of strings, instead they are
        # tuples of complex objects and therefore can neither be decoded
        # nor hashed (ie can't use 'set')
        decoded_items = (
            set(map(bytes.decode, non_empty_items))
            if field_name != PARSED_MODIFICATION_KEY
            else list(non_empty_items)
        )

        if decoded_items:
            decoded_record[field_name.lower()] = decoded_items
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
            if field_name != PARSED_MODIFICATION_KEY
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


class _StreamBlock(Protocol):
    def flush(self) -> str: ...
    def reset(self): ...
    def parse(self, line: bytes): ...
    def __bool__(self): ...


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

    def reset(self):
        self.buffer = bytes()
        self.keep = False

    def parse(self, line: bytes):
        if not self.keep and any(filter(line) for filter in self.filters):
            self.keep = True
        self.buffer += line

    def __bool__(self):
        return bool(self.buffer) and self.keep


class GroupedStreamBlock:
    def __init__(self, group_field: str, filter_terms: list[tuple[str, str]]):
        self.data = defaultdict(BytesIO)
        self.filters: list[FunctionType] = [
            re.compile(rf"(?i)^({key}): ({value})\n$".encode()).match
            for key, value in filter_terms
        ]
        self.group_filter = re.compile(rf"(?i)^({group_field}): (.*)\n$".encode()).match
        self.group_filter_base_64 = re.compile(
            rf"(?i)^({group_field}):: (.*)\n$".encode()
        ).match
        self.reset()

    def flush(self) -> str:
        if self.group is None:
            raise ValueError(
                f"No group name assigned to the following group:\n{self.buffer}"
            )
        self.data[self.group].write(self.buffer)
        self.reset()

    def reset(self) -> str:
        self.buffer = bytes()
        self.keep = False
        self.group = None

    def parse(self, line: bytes):
        group_match = self.group_filter(line)
        if group_match:
            (_, self.group) = group_match.groups()
        else:
            b64_group_match = self.group_filter_base_64(line)
            if b64_group_match:
                (_, b64_group) = b64_group_match.groups()
                self.group = b64decode(b64_group).strip()

        if not self.keep and any(filter(line) for filter in self.filters):
            self.keep = True
        self.buffer += line

    def __bool__(self):
        return bool(self.buffer) and self.keep


def stream_to_block(s3_path: str, s3_client: "S3Client", stream_block: _StreamBlock):
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
    stream_to_block(s3_path=s3_path, s3_client=s3_client, stream_block=stream_block)
    return stream_block.data.getbuffer()


def filter_and_group_ldif_from_s3_by_property(
    s3_path,
    group_field: str,
    filter_terms: list[tuple[str, str]],
    s3_client: "S3Client",
) -> Generator[memoryview, None, None]:
    """
    Efficiently streams a file from S3 directly into a bytes memoryview,
    filtering out any LDIF record without any (attribute_name, attribute_value)
    matching at least one of the filter terms, and then also grouping records
    by the group_field.

    The output of this function can then be parsed using'
    'parse_ldif(file_opener=BytesIO, path_or_data=filtered_and_grouped_ldif)'
    """

    stream_block = GroupedStreamBlock(
        group_field=group_field, filter_terms=filter_terms
    )
    stream_to_block(s3_path=s3_path, s3_client=s3_client, stream_block=stream_block)

    for group in stream_block.data.values():
        yield group.getbuffer()
