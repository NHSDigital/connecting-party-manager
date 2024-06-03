"""
A script that filters and removes objects from an LDIF that won't pass the ETL.
Useful for cleaning up the INT bulk data.

This script isn't particularly intended to have a long life. General instructions are to either do:

    ldif_cleanup("local/path/to/file.ldif")

or (slower)

    ldif_cleanup("s3://path/to/file.ldif", boto3.client("s3"))

and it will save a file in your root dir called 'good.ldif' that has only good
nhsMhs and nhsAccreditedSystem objects in them, i.e. those which are guaranteed
to be successfully processed by the ETL.

It's not particularly optimised, either timewise or memorywise, so:
* you better have some ok memory on your laptop,
* it'll take a few minutes

Oh, and you'll need to install 'tqdm', thanks!
"""

import json
from collections import deque
from io import BytesIO
from pathlib import Path

from domain.core.load_questionnaire import render_questionnaire
from domain.core.questionnaires import QuestionnaireInstance
from etl_utils.io import EtlEncoder
from etl_utils.ldif.ldif import filter_ldif_from_s3_by_property, parse_ldif
from etl_utils.worker.action import apply_action
from event.json import json_loads
from mypy_boto3_s3 import S3Client
from sds.cpm_translation import translate
from sds.domain.constants import FILTER_TERMS
from sds.domain.parse import parse_sds_record
from tqdm import tqdm


def ldif_cleanup(s3_input_path: str, s3_client: S3Client) -> Path:
    filtered_ldif = filter_ldif_from_s3_by_property(
        s3_path=s3_input_path, filter_terms=FILTER_TERMS, s3_client=s3_client
    )

    spine_device_questionnaire = render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_DEVICE, questionnaire_version=1
    )
    spine_endpoint_questionnaire = render_questionnaire(
        questionnaire_name=QuestionnaireInstance.SPINE_ENDPOINT, questionnaire_version=1
    )

    _spine_device_questionnaire = spine_device_questionnaire.dict()
    _spine_endpoint_questionnaire = spine_endpoint_questionnaire.dict()

    all_keys = set()

    good_rows = []
    for row in tqdm(filtered_ldif.tobytes().split(b"\n\n")):
        unprocessed_records = deque(parse_ldif(file_opener=BytesIO, path_or_data=row))
        processed_records = deque()

        exception = apply_action(
            unprocessed_records=unprocessed_records,
            processed_records=processed_records,
            action=lambda record: parse_sds_record(*record).dict(),
            record_serializer=lambda dn_and_record: json_loads(
                json.dumps(dn_and_record[1], cls=EtlEncoder)
            ),
        )
        if exception:
            raise exception

        processed_transform_records = deque()
        exception = apply_action(
            unprocessed_records=processed_records,
            processed_records=processed_transform_records,
            action=lambda record: translate(
                obj=record,
                spine_device_questionnaire=spine_device_questionnaire,
                _spine_device_questionnaire=_spine_device_questionnaire,
                spine_endpoint_questionnaire=spine_endpoint_questionnaire,
                _spine_endpoint_questionnaire=_spine_endpoint_questionnaire,
                _trust=True,
                repository=None,
            ),
        )
        if exception:
            continue

        is_duplicate = False
        for transform_events in processed_transform_records:
            ((_, event),) = transform_events.items()
            device_key = event.get("key")
            if device_key:
                is_duplicate = device_key in all_keys
                all_keys.add(device_key)
            if is_duplicate:
                break

        if not is_duplicate:
            good_rows.append(row)

    with open("good.ldif", "w") as f:
        f.write(b"\n\n".join(good_rows).decode())


if __name__ == "__main__":
    ldif_cleanup(s3_input_path="~/Downloads/538684.ldif", s3_client=None)
