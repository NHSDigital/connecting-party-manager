import re
import sys
from itertools import chain
from pathlib import Path

LD_LIBRARIES = set(map(str, Path("/lib64/").iterdir()))
LD_LIBRARIES_REGEX = r"\/lib64\/(lib.*)\.so.*"
LD_LIBRARIES_PATTERN = re.compile(LD_LIBRARIES_REGEX)


def parse_ld_output(terms):
    """
    'terms' is the output of the shell command

        LD_TRACE_LOADED_OBJECTS=1 /lib64/ld-linux-x86-64.so.2 <shared_object>

    which gives the full dependency tree for a given <shared_object>
    """
    filtered_terms = filter(bool, map(LD_LIBRARIES_PATTERN.match, terms))
    short_library_names = set(chain.from_iterable(map(re.Match.groups, filtered_terms)))
    full_library_names = (
        library
        for library in LD_LIBRARIES
        if any(name in library for name in short_library_names)
    )
    print(" ".join(full_library_names))  # noqa: T201


if __name__ == "__main__":
    parse_ld_output(terms=sys.argv[1:])
