from domain.core.cpm_product.v1 import CpmProductEventDeserializer
from domain.core.device.v1 import DeviceEventDeserializer
from domain.core.device_reference_data.v1 import DeviceReferenceDataEventDeserializer
from domain.core.event import Event, ExportedEventTypeDef
from domain.core.product_team.v1 import ProductTeamEventDeserializer


def deserialize_event(event: ExportedEventTypeDef) -> Event:
    for deserializer in (
        ProductTeamEventDeserializer,
        CpmProductEventDeserializer,
        DeviceEventDeserializer,
        DeviceReferenceDataEventDeserializer,
    ):
        try:
            return (deserializer, deserializer.parse(event))
        except Exception as exception:
            pass
    return exception
