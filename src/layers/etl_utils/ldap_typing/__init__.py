from typing import Protocol


class LdapClientProtocol(Protocol):
    def search(self, base: str, scope: str, filterstr="", attrlist=[]):
        ...

    def result(self) -> tuple[int, list[tuple[str, dict[str, list[str]]]]]:
        ...

    def set_option(self, option: str, invalue: str):
        ...

    def simple_bind_s(self, who=None, cred=None):
        ...


class LdapModuleProtocol(Protocol):
    OPT_X_TLS_CERTFILE: int
    OPT_X_TLS_KEYFILE: int
    OPT_X_TLS_REQUIRE_CERT: int
    OPT_X_TLS_ALLOW: int
    OPT_X_TLS_NEWCTX: int

    SCOPE_BASE: str
    SCOPE_ONELEVEL: str

    def initialize(self, host: str) -> LdapClientProtocol:
        ...
