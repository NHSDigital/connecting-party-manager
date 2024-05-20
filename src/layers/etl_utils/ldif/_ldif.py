"""
Downloaded, pruned and modified from https://raw.githubusercontent.com/python-ldap/python-ldap/main/Lib/ldif.py

The only modifications were (search this file for '**We modified this**'):
    * yield records in parse(), rather than append.
    * lowercase all attribute names
Other than that, unnecessary features were removed.
"""

__version__ = "3.4.4"

import re
from base64 import b64decode, b64encode
from collections import defaultdict
from typing import IO
from urllib.parse import urlparse
from urllib.request import urlopen

attrtype_pattern = r"[\w;.-]+(;[\w_-]+)*"
attrvalue_pattern = r'(([^,]|\\,)+|".*?")'
attrtypeandvalue_pattern = attrtype_pattern + r"[ ]*=[ ]*" + attrvalue_pattern
rdn_pattern = (
    attrtypeandvalue_pattern + r"([ ]*\+[ ]*" + attrtypeandvalue_pattern + r")*[ ]*"
)
dn_pattern = rdn_pattern + r"([ ]*,[ ]*" + rdn_pattern + r")*[ ]*"
dn_regex = re.compile("^%s$" % dn_pattern)

SAFE_STRING_PATTERN = b"(^(\000|\n|\r| |:|<)|[\000\n\r\200-\377]+|[ ]+$)"  # NOSONAR
safe_string_re = re.compile(SAFE_STRING_PATTERN)


CHANGE_TYPES = {"add", "delete", "modify"}  # ,'modrdn'
MODIFICATION_OPERATIONS = {"add", "delete", "replace"}


def is_dn(s):
    """
    returns 1 if s is a LDAP DN
    """
    if s == "":
        return 1
    rm = dn_regex.match(s)
    return rm != None and rm.group(0) == s


def list_dict(l):
    """
    return a dictionary with all items of l being the keys of the dictionary
    """
    return {i: None for i in l}


class LDIFParser:
    """
    Base class for a LDIF parser. Applications should sub-class this
    class and override method handle() to implement something meaningful.

    Public class attributes:

    records_read
          Counter for records processed so far
    """

    def __init__(
        self,
        input_file: IO,
        ignored_attr_types: list[str] = None,
        max_entries=0,
        process_url_schemes: list[str] = None,
        line_sep="\n",
    ):
        """
        Parameters:
        input_file
            File-object to read the LDIF input from
        ignored_attr_types
            Attributes with these attribute type names will be ignored.
        max_entries
            If non-zero specifies the maximum number of entries to be
            read from f.
        process_url_schemes
            List containing strings with URLs schemes to process with urllib.
            An empty list turns off all URL processing and the attribute
            is ignored completely.
        line_sep
            String used as line separator
        """
        self._input_file = input_file
        # Detect whether the file is open in text or bytes mode.
        self._file_sends_bytes = isinstance(self._input_file.read(0), bytes)
        self._max_entries = max_entries
        self._process_url_schemes = list_dict(
            [s.lower() for s in (process_url_schemes or [])]
        )
        self._ignored_attr_types = list_dict(
            [a.lower() for a in (ignored_attr_types or [])]
        )
        self._last_line_sep = line_sep
        self.version = None
        # Initialize counters
        self.line_counter = 0
        self.byte_counter = 0
        self.records_read = 0
        self.changetype_counter = {}.fromkeys(CHANGE_TYPES, 0)
        # Store some symbols for better performance
        self._b64decode = b64decode
        # Read very first line
        try:
            self._last_line = self._readline()
        except EOFError:
            self._last_line = ""

    def _readline(self):
        s = self._input_file.readline()
        if self._file_sends_bytes:
            # The RFC does not allow UTF-8 values; we support it as a
            # non-official, backwards compatibility layer
            s = s.decode("utf-8")
        self.line_counter = self.line_counter + 1
        self.byte_counter = self.byte_counter + len(s)
        if not s:
            return None
        elif s[-2:] == "\r\n":
            return s[:-2]
        elif s[-1:] == "\n":
            return s[:-1]
        else:
            return s

    def _unfold_lines(self):
        """
        Unfold several folded lines with trailing space into one line
        """
        if self._last_line is None:
            raise EOFError(
                "EOF reached after %d lines (%d bytes)"
                % (
                    self.line_counter,
                    self.byte_counter,
                )
            )
        unfolded_lines = [self._last_line]
        next_line = self._readline()
        while next_line and next_line[0] == " ":
            unfolded_lines.append(next_line[1:])
            next_line = self._readline()
        self._last_line = next_line
        return "".join(unfolded_lines)

    def _next_key_and_value(self, raise_on_eof=False):
        try:
            return self.__next_key_and_value()
        except EOFError:
            if raise_on_eof:
                raise
            return None, None

    def __next_key_and_value(self):
        """
        Parse a single attribute type and value pair from one or
        more lines of LDIF data

        Returns attr_type (text) and attr_value (bytes)
        """
        # Reading new attribute line
        unfolded_line = self._unfold_lines()
        # Ignore comments which can also be folded
        while unfolded_line and unfolded_line[0] == "#":
            unfolded_line = self._unfold_lines()
        if not unfolded_line:
            return None, None
        if unfolded_line == "-":
            return "-", None
        try:
            colon_pos = unfolded_line.index(":")
        except ValueError as e:
            raise ValueError("no value-spec in %s" % (repr(unfolded_line)))
        attr_type = unfolded_line[0:colon_pos]
        # if needed attribute value is BASE64 decoded
        value_spec = unfolded_line[colon_pos : colon_pos + 2]
        if value_spec == ": ":
            attr_value = unfolded_line[colon_pos + 2 :].lstrip()
            # All values should be valid ascii; we support UTF-8 as a
            # non-official, backwards compatibility layer.
            attr_value = attr_value.encode("utf-8")
        elif value_spec == "::":
            # attribute value needs base64-decoding
            # base64 makes sens only for ascii
            attr_value = unfolded_line[colon_pos + 2 :]
            attr_value = attr_value.encode("ascii")
            attr_value = self._b64decode(attr_value)
        elif value_spec == ":<":
            # fetch attribute value from URL
            url = unfolded_line[colon_pos + 2 :].strip()
            attr_value = None
            if self._process_url_schemes:
                u = urlparse(url)
                if u[0] in self._process_url_schemes:
                    attr_value = urlopen(url).read()
        else:
            # All values should be valid ascii; we support UTF-8 as a
            # non-official, backwards compatibility layer.
            attr_value = unfolded_line[colon_pos + 1 :].encode("utf-8")
        return attr_type.lower(), attr_value

    def _consume_empty_lines(self):
        """
        Consume empty lines until first non-empty line.
        Must only be used between full records!

        Returns non-empty key-value-tuple.
        """
        k, v = self._next_key_and_value()
        while k is None and v is None:
            try:
                k, v = self._next_key_and_value(raise_on_eof=True)
            except EOFError:
                break
        return k, v

    def _parse_header(self):
        # Consume empty lines
        k, v = self._consume_empty_lines()
        # Consume 'version' line
        if k == "version":
            self.version = int(v.decode("ascii"))
            k, v = self._consume_empty_lines()
        return k, v

    def _parse_dn(self, k: str, v: bytes):
        if k != "dn":
            raise ValueError(
                'Line %d: First line of record does not start with "dn:": %s'
                % (self.line_counter, repr(k))
            )
        # Value of a 'dn' field *has* to be valid UTF-8
        # k is text, v is bytes.
        v = v.decode("utf-8")
        if not is_dn(v):
            raise ValueError(
                "Line %d: Not a valid string-representation for dn: %s."
                % (self.line_counter, repr(v))
            )
        return v

    def _parse_changetype(self, k, v):
        if k == "changetype":
            # v is still bytes, spec says it should be valid utf-8; decode it.
            v = v.decode("utf-8")
            if not v in CHANGE_TYPES:
                raise ValueError("Invalid changetype: %s" % repr(v))
            return v
        return None

    def _parse_modify(self):
        modifications = defaultdict(list)
        modifications["changetype"].append(b"modify")
        modifications["modifications"] = []

        k, v = self._next_key_and_value()
        # Loop for reading the list of modifications
        while k != None:
            # Extract attribute mod-operation (add, delete, replace)
            if k not in MODIFICATION_OPERATIONS:
                modifications[k].append(v)
                k, v = self._next_key_and_value()
                continue
            modification_operation = k

            # we now have the attribute name to be modified
            # v is still bytes, spec says it should be valid utf-8; decode it.
            v = v.decode("utf-8")
            attribute_name = v.lower()
            new_values = set()
            k, v = self._next_key_and_value()
            while k == attribute_name:
                new_values.add(v.decode())
                k, v = self._next_key_and_value()

            modifications["modifications"].append(
                (modification_operation, attribute_name, new_values)
            )

            if k == "-":  # skip hyphens
                k, v = self._next_key_and_value()
        return modifications

    def _parse_entry(self, k, v):
        entry = defaultdict(list)

        # Loop for reading the attributes
        while k != None:
            # Add the attribute to the entry if not ignored attribute
            if not k.lower() in self._ignored_attr_types:
                entry[k].append(v)
            k, v = self._next_key_and_value()
        return entry

    def parse(self):
        """
        Continuously read and parse LDIF entry records
        """
        k, v = self._parse_header()

        # Loop for processing whole records
        while k != None and (
            not self._max_entries or self.records_read < self._max_entries
        ):
            # Consume first line which must start with "dn: "
            dn = self._parse_dn(k, v)
            # Consume second line of record
            k, v = self._next_key_and_value()

            # Determine changetype first
            changetype = self._parse_changetype(k, v)
            if changetype == "modify":
                entry = self._parse_modify()
            else:
                entry = self._parse_entry(k, v)
            yield (dn, entry)

            # Consume empty separator line(s)
            k, v = self._consume_empty_lines()
        return


class LDIFWriter:
    """
    Write LDIF entry or change records to file object
    Copy LDIF input to a file output object containing all data retrieved
    via URLs
    """

    def __init__(self, output_file: IO, base64_attrs=None, cols=76, line_sep="\n"):
        """
        output_file
            file object for output; should be opened in *text* mode
        base64_attrs
            list of attribute types to be base64-encoded in any case
        cols
            Specifies how many columns a line may have before it's
            folded into many lines.
        line_sep
            String used as line separator
        """
        self._output_file = output_file
        self._base64_attrs = list_dict([a.lower() for a in (base64_attrs or [])])
        self._cols = cols
        self._last_line_sep = line_sep
        self.records_written = 0

    def _unfold_lines(self, line: str):
        """
        Write string line as one or more folded lines
        """
        # Check maximum line length
        line_len = len(line)
        if line_len <= self._cols:
            self._output_file.write(line.encode())
            self._output_file.write(self._last_line_sep.encode())
        else:
            # Fold line
            pos = self._cols
            self._output_file.write(line[0 : min(line_len, self._cols)].encode())
            self._output_file.write(self._last_line_sep.encode())
            while pos < line_len:
                self._output_file.write(" ".encode())
                self._output_file.write(
                    line[pos : min(line_len, pos + self._cols - 1)].encode()
                )
                self._output_file.write(self._last_line_sep.encode())
                pos = pos + self._cols - 1
        return  # _unfold_lines()

    def _needs_base64_encoding(self, attr_type, attr_value):
        """
        returns 1 if attr_value has to be base-64 encoded because
        of special chars or because attr_type is in self._base64_attrs
        """
        return (
            attr_type.lower() in self._base64_attrs
            or not safe_string_re.search(attr_value) is None
        )

    def _unparseAttrTypeandValue(self, attr_type, attr_value):
        """
        Write a single attribute type/value pair

        attr_type
              attribute type (text)
        attr_value
              attribute value (bytes)
        """
        if self._needs_base64_encoding(attr_type, attr_value):
            # Encode with base64
            encoded = b64encode(attr_value).decode("ascii")
            encoded = encoded.replace("\n", "")
            self._unfold_lines(":: ".join([attr_type, encoded]))
        else:
            self._unfold_lines(": ".join([attr_type, attr_value.decode("ascii")]))
        return  # _unparseAttrTypeandValue()

    def _unparseEntryRecord(self, entry):
        """
        entry
            dictionary holding an entry
        """
        for attr_type, values in sorted(entry.items()):
            if attr_type == "modifications":
                for modification_operation, attribute_name, new_values in values:
                    self._unfold_lines(f"{modification_operation}: {attribute_name}")
                    for v in sorted(new_values):
                        self._unfold_lines(f"{attribute_name}: {v}")
                    self._unfold_lines("-")

            else:
                for attr_value in values:
                    self._unparseAttrTypeandValue(attr_type, attr_value)

    def unparse(self, dn: str, record):
        """
        dn
              string-representation of distinguished name
        record
              Either a dictionary holding the LDAP entry {attrtype:record}
              or a list with a modify list like for LDAPObject.modify().
        """
        # Start with line containing the distinguished name
        dn = dn.encode("utf-8")
        self._unparseAttrTypeandValue("dn", dn)
        self._unparseEntryRecord(record)
        # Write empty line separating the records
        self._output_file.write(self._last_line_sep.encode())
        # Count records written
        self.records_written = self.records_written + 1
        return
