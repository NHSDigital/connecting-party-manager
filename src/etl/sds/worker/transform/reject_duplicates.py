import json
from collections import defaultdict
from typing import DefaultDict, Generator

from domain.core.event import ExportedEventsTypeDef
from etl_utils.io import EtlEncoder


class DuplicateSdsKey(Exception):
    pass


def _get_duplicate_events(
    exported_events: ExportedEventsTypeDef,
) -> Generator[tuple[str, list[list[dict]]], None, None]:
    ids_by_key: DefaultDict[str, list[str]] = defaultdict(list)
    events_by_id: DefaultDict[str, list[dict]] = defaultdict(list)
    for exported_event in exported_events:
        ((_, event),) = exported_event.items()
        event_id = event.get("id") or event.get("entity_id")
        device_key = event.get("key")
        events_by_id[event_id].append(event)
        if device_key:
            ids_by_key[device_key].append(event_id)

    for device_key, event_ids in ids_by_key.items():
        if len(event_ids) == 1:
            continue

        yield (
            device_key,
            list(events_by_id[_event_id] for _event_id in event_ids),
        )


def reject_duplicate_keys(exported_events: ExportedEventsTypeDef):
    error_message = "\n".join(
        "\n".join(
            (
                f"Duplicates found for device key '{device_key}'",
                *(json.dumps(duplicates[0], cls=EtlEncoder),),
                "===============",
            )
        )
        for device_key, duplicates in _get_duplicate_events(
            exported_events=exported_events
        )
    )
    if error_message:
        raise DuplicateSdsKey(error_message)
