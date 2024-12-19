from domain.core.cpm_product.v1 import CpmProductEventDeserializer
from domain.core.device.v1 import DeviceEventDeserializer
from domain.core.device_reference_data.v1 import DeviceReferenceDataEventDeserializer
from domain.core.event import Event, ExportedEventTypeDef
from domain.core.product_team.v1 import ProductTeamEventDeserializer
from sds.epr.updates.etl_device import EtlDeviceEventDeserializer


class EventDeserializationError(Exception): ...


def deserialize_event(event: ExportedEventTypeDef) -> Event:
    exceptions = []
    for deserializer in (
        ProductTeamEventDeserializer,
        CpmProductEventDeserializer,
        DeviceEventDeserializer,
        DeviceReferenceDataEventDeserializer,
        EtlDeviceEventDeserializer,
    ):
        try:
            return (deserializer, deserializer.parse(event))
        except Exception as exception:
            exceptions.append(exception)
    raise ExceptionGroup(f"Could not deserialise {event}", exceptions)
