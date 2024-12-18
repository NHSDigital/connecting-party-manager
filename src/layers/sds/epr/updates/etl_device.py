from attr import dataclass
from domain.core.device.v1 import Device
from domain.core.event import Event, EventDeserializer


@dataclass(kw_only=True, slots=True)
class DeviceHardDeletedEvent(Event):
    id: str
    keys: list[dict]
    tags: list[str]


class EtlDevice(Device):
    def hard_delete(self) -> DeviceHardDeletedEvent:
        event = DeviceHardDeletedEvent(
            id=str(self.id),
            keys=[k.dict() for k in self.keys],
            tags=sorted(t.value for t in self.tags),
        )
        self.events.append(event)
        return event


class EtlDeviceEventDeserializer(EventDeserializer):
    event_types = (DeviceHardDeletedEvent,)
