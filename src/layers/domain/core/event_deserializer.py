from domain.core.cpm_product.v1 import CpmProductEventDeserializer
from domain.core.event import Event, ExportedEventTypeDef
from domain.core.product_team.v1 import ProductTeamEventDeserializer


def deserialize_event(event: ExportedEventTypeDef) -> Event:
    exceptions = []
    for deserializer in (
        ProductTeamEventDeserializer,
        CpmProductEventDeserializer,
    ):
        try:
            return (deserializer, deserializer.parse(event))
        except Exception as exception:
            exceptions.append(exception)
    raise ExceptionGroup(f"Could not deserialise {event}", exceptions)
