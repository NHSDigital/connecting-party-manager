import pytest
from domain.core.timestamp import now
from etl_utils.ldif.model import DistinguishedName
from sds.domain.nhs_accredited_system import NhsAccreditedSystem
from sds.domain.nhs_mhs import NhsMhs


@pytest.fixture
def mhs_1() -> NhsMhs:
    return NhsMhs(
        _distinguished_name=DistinguishedName(
            parts=(("ou", "services"), ("uniqueidentifier", "1wd354"), ("o", "nhs"))
        ),
        objectclass={"nhsmhs"},
        nhsidcode="AAA",
        nhsproductname="My EPR Product",
        nhsmhspartykey="AAA-123456",
        nhsmhssvcia="my-interaction-id",
        nhsmhsendpoint="my-mhs-endpoint",
        uniqueidentifier="1wd354",
        nhsapproverurp="approver-123",
        nhscontractpropertytemplatekey="key-123",
        nhsdateapproved="today",
        nhsdatednsapproved="yesterday",
        nhsdaterequested="a week ago",
        nhsdnsapprover="dns-approver-123",
        nhsepinteractiontype="hl7",
        nhsmhscpaid="1wd354",
        nhsmhsfqdn="my-fqdn",
        nhsmhsin="in-123",
        nhsmhsisauthenticated="none",
        nhsmhssn="sn-123",
        nhsproductkey="key-123",
        nhsrequestorurp="requester-123",
        nhsmhsmanufacturerorg="AAA",
    )


@pytest.fixture
def mhs_2() -> NhsMhs:
    return NhsMhs(
        _distinguished_name=DistinguishedName(
            parts=(("ou", "services"), ("uniqueidentifier", "h0394j"), ("o", "nhs"))
        ),
        objectclass={"nhsmhs"},
        nhsidcode="BBB",
        nhsproductname="My Other EPR Product",
        nhsmhspartykey="BBB-123456",
        nhsmhssvcia="my-other-interaction-id",
        nhsmhsendpoint="my-other-mhs-endpoint",
        uniqueidentifier="h0394j",
        nhsapproverurp="approver-456",
        nhscontractpropertytemplatekey="key-456",
        nhsdateapproved="today",
        nhsdatednsapproved="yesterday",
        nhsdaterequested="a week ago",
        nhsdnsapprover="dns-approver-456",
        nhsepinteractiontype="hl7",
        nhsmhscpaid="h0394j",
        nhsmhsfqdn="my-fqdn",
        nhsmhsin="in-456",
        nhsmhsisauthenticated="none",
        nhsmhssn="sn-456",
        nhsproductkey="key-456",
        nhsrequestorurp="requester-456",
        nhsmhsmanufacturerorg="AAA",
    )


@pytest.fixture
def accredited_system_1() -> NhsMhs:
    return NhsAccreditedSystem(
        _distinguished_name=DistinguishedName(
            parts=(("ou", "services"), ("uniqueidentifier", "1wd354"), ("o", "nhs"))
        ),
        objectclass={"nhsas"},
        uniqueidentifier="123456",
        nhsapproverurp="approver-123",
        nhsrequestorurp="requester-123",
        nhsdaterequested="a week ago",
        nhsdateapproved="today",
        nhsidcode="AAA",
        nhsmhspartykey="AAA-123456",
        nhsproductkey="key-123",
        nhsasclient={"ABC", "CDE", "EFG"},
        nhsassvcia={"interaction-id-1", "interaction-id-2"},
        nhsmhsmanufacturerorg="AAA",
    )


@pytest.fixture
def accredited_system_2() -> NhsMhs:
    return NhsAccreditedSystem(
        _distinguished_name=DistinguishedName(
            parts=(("ou", "services"), ("uniqueidentifier", "1wd354"), ("o", "nhs"))
        ),
        objectclass={"nhsas"},
        uniqueidentifier="456789",
        nhsapproverurp="approver-456",
        nhsrequestorurp="requester-456",
        nhsdaterequested="a week ago",
        nhsdateapproved="today",
        nhsidcode="BBB",
        nhsmhspartykey="AAA-456789",
        nhsproductkey="key-123",
        nhsasclient={"ABC", "JKL", "LMN"},
        nhsassvcia={"interaction-id-2", "interaction-id-4"},
        nhsmhsmanufacturerorg="AAA",
    )


@pytest.fixture(scope="module")
def today_string():
    return now().date().isoformat()
