from uuid import UUID

DEFAULT_ORGANISATION = "CDEF"

DEFAULT_PRODUCT_TEAM = {
    "id": UUID(int=0x12345678123456781234567812345678),
    "name": "ROOT",
}

EXCEPTIONAL_ODS_CODES = {
    "696B001",
    "TESTEBS1",
    "TESTLSP0",
    "TESTLSP1",
    "TESTLSP3",
    "TMSAsync1",
    "TMSAsync2",
    "TMSAsync3",
    "TMSAsync4",
    "TMSAsync5",
    "TMSAsync6",
    "TMSEbs2",
}

BAD_UNIQUE_IDENTIFIERS = {
    "31af51067f47f1244d38",  # pragma: allowlist secret
    "a83e1431f26461894465",  # pragma: allowlist secret
    "S2202584A2577603",
    "S100049A300185",
}
