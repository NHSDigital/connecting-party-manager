from domain.core.device import Device
from domain.repository.repository import Repository

from .mock_search_responses.mock_responses import (
    device_5NR_result,
    device_RTX_result,
    endpoint_5NR_result,
    endpoint_RTX_result,
    no_device_results,
    no_endpoint_results,
)


class DeviceRepository(Repository[Device]):
    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name, model=Device, dynamodb_client=dynamodb_client
        )

    def query_by_tag(self, tags, **kwargs):
        if "nhs_as_client" in tags:
            if tags["nhs_as_client"] != "5NR" and tags["nhs_as_client"] != "RTX":
                return no_device_results
            else:
                if tags["nhs_as_client"] == "5NR":
                    return device_5NR_result
                if tags["nhs_as_client"] == "RTX":
                    return device_RTX_result
        else:
            if "nhs_id_code" in tags:
                if tags["nhs_id_code"] != "5NR" and tags["nhs_id_code"] != "RTX":
                    return no_endpoint_results
                else:
                    if tags["nhs_id_code"] == "5NR":
                        return endpoint_5NR_result
                    if tags["nhs_id_code"] == "RTX":
                        return endpoint_RTX_result
            else:
                if "nhs_mhs_party_key" in tags:
                    if tags["nhs_mhs_party_key"] == "D81631-827817":
                        return endpoint_RTX_result
                    else:
                        return no_endpoint_results
                else:
                    return no_endpoint_results
