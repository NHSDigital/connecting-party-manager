import json
from collections import defaultdict
from itertools import chain
from typing import Generator

from domain.core.device import DeviceKeyAddedEvent
from domain.core.event import ExportedEventsTypeDef
from etl_utils.io import EtlEncoder


class DuplicateSdsKey(Exception):
    pass


def _get_duplicate_events(
    exported_events: ExportedEventsTypeDef,
) -> Generator[tuple[str, list[list[dict]]], None, None]:
    device_ids_by_device_key = defaultdict(set)
    events_by_id = defaultdict(list)

    for exported_event in exported_events:
        ((event_name, event),) = exported_event.items()
        if event_name != DeviceKeyAddedEvent.public_name:
            continue

        device_id = event["id"]
        device_key = event["key"]
        device_ids_by_device_key[device_key].add(device_id)
        events_by_id[device_id].append(event)

    for device_key, event_ids in device_ids_by_device_key.items():
        if len(event_ids) == 1:
            continue
        events_for_this_key = chain.from_iterable(
            events_by_id[_event_id] for _event_id in event_ids
        )
        yield (device_key, list(events_for_this_key))


def reject_duplicate_keys(exported_events: ExportedEventsTypeDef):
    error_message = "\n".join(
        "\n".join(
            (
                f"Duplicates found for device key '{device_key}'",
                *(json.dumps(duplicates, cls=EtlEncoder),),
                "===============",
            )
        )
        for device_key, duplicates in _get_duplicate_events(
            exported_events=exported_events
        )
    )
    if error_message:
        raise DuplicateSdsKey(error_message)
