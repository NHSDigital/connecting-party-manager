from typing import Mapping


class FrozenDict(Mapping):
    """An implementation of a frozen dict, lifted from https://stackoverflow.com/a/2704866/1571593"""

    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._hash = None

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __str__(self):
        return str(self._d)

    def __repr__(self):
        return repr(self._d)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FrozenDict):
            return other._d == self._d
        return False

    def __hash__(self):
        # It would have been simpler and maybe more obvious to
        # use hash(tuple(sorted(self._d.iteritems()))) from this discussion
        # so far, but this solution is O(n). I don't know what kind of
        # n we are going to run into, but sometimes it's hard to resist the
        # urge to optimize when it will gain improved algorithmic performance.
        if self._hash is None:
            hash_ = 0
            for pair in self.items():
                hash_ ^= hash(pair)
            self._hash = hash_
        return self._hash
