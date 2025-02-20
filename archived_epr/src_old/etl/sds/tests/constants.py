BULK_TEST_CHANGELOG_NUMBER = "1701246"
BULK_TEST_BASE_PATH = "sds/etl/bulk/test"
CHANGELOG_TEST_BASE_PATH = "sds/etl/changelog"


class EtlTestDataPath:
    FULL_LDIF = f"{BULK_TEST_BASE_PATH}/{BULK_TEST_CHANGELOG_NUMBER}-full.ldif"  # input to extract
    FULL_JSON = f"{BULK_TEST_BASE_PATH}/{BULK_TEST_CHANGELOG_NUMBER}-full.json"  # input to transform
    MINI_LDIF = f"{BULK_TEST_BASE_PATH}/{BULK_TEST_CHANGELOG_NUMBER}-mini.ldif"  # input to extract
    CHANGELOG = f"{CHANGELOG_TEST_BASE_PATH}/75852519.ldif"
