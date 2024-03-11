import ldap

HOST = "ldap://ldap.forumsys.com"
THE_PASSWORD = "password"  # pragma: allowlist secret
DN = "uid=tesla,dc=example,dc=com"
BASE_SEARCH = "dc=example,dc=com"


def handler(event, context):
    ldap_connection = ldap.initialize(HOST)
    ldap_connection.simple_bind_s(DN, THE_PASSWORD)
    ldap_connection.search(
        base=BASE_SEARCH,
        scope=ldap.SCOPE_SUBTREE,
    )
    return ldap_connection.result()
