from typing import List
from uuid import uuid4

from domain.core.device import Device as DomainDevice
from domain.core.product_team import ProductTeam
from domain.fhir.r4 import Device as FhirDevice
from domain.fhir.r4 import StrictDevice as StrictFhirDevice
from domain.fhir.r4.cpm_model import SYSTEM, Answer, CollectionBundle
from domain.fhir.r4.cpm_model import Device as CpmFhirDevice
from domain.fhir.r4.cpm_model import (
    DeviceDefinitionIdentifier,
    DeviceDefinitionReference,
    DeviceIdentifier,
    DeviceName,
    DeviceOwnerReference,
    Link,
    ProductTeamIdentifier,
    QuestionAndAnswer,
)
from domain.fhir.r4.cpm_model import (
    QuestionnaireResponse as CpmFhirQuestionnaireResponse,
)
from domain.fhir.r4.cpm_model import Reference, Resource, SearchsetBundle
from domain.fhir_translation.parse import create_fhir_model_from_fhir_json
from domain.response.validation_errors import mark_validation_errors_as_inbound


@mark_validation_errors_as_inbound
def parse_fhir_device_json(fhir_device_json: dict) -> CpmFhirDevice:
    fhir_device = create_fhir_model_from_fhir_json(
        fhir_json=fhir_device_json,
        fhir_models=[FhirDevice, StrictFhirDevice],
        our_model=CpmFhirDevice,
    )
    return fhir_device


def create_domain_device_from_fhir_device(
    fhir_device: CpmFhirDevice, product_team: ProductTeam
) -> DomainDevice:
    (device_name,) = fhir_device.deviceName
    device = product_team.create_device(
        name=device_name.name,
        type=fhir_device.definition.identifier.value,
    )
    for identifier in fhir_device.identifier:
        device.add_key(type=identifier.key_type, key=identifier.value)
    return device


def create_fhir_model_from_device(device: DomainDevice) -> CpmFhirDevice:
    return CpmFhirDevice(
        resourceType=CpmFhirDevice.__name__,
        deviceName=[DeviceName(name=device.name)],
        definition=DeviceDefinitionReference(
            identifier=DeviceDefinitionIdentifier(value=device.type)
        ),
        identifier=[
            DeviceIdentifier(system=f"{SYSTEM}/{key.type}", value=key.key)
            for key in device.keys.values()
        ],
        owner=DeviceOwnerReference(
            identifier=ProductTeamIdentifier(value=device.product_team_id)
        ),
    )


def create_fhir_model_from_questionnaire_response(
    device: DomainDevice,
) -> CpmFhirQuestionnaireResponse:
    items = []
    for identifier, responses in device.questionnaire_responses.items():
        for questionnaire_response in responses:
            for ques_res in questionnaire_response.responses:
                for question, answers in ques_res.items():
                    answer_objects = [Answer(valueString=answer) for answer in answers]
                    question_and_answer = QuestionAndAnswer(
                        link_id=question, text=question, answer=answer_objects
                    )
                    items.append(question_and_answer)

    return CpmFhirQuestionnaireResponse(
        resourceType=CpmFhirQuestionnaireResponse.__name__,
        # identifier="010057927542",
        # questionnaire="https://cpm.co.uk/Questionnaire/spine_device|v1", Doesn't exist yet
        subject=Reference(reference=f"https://cpm.co.uk/Device/{device.id}"),
        # "authored": "<dateTime>",
        author=Reference(
            reference=f"https://cpm.co.uk/Organization/{device.product_team_id}"
        ),
        item=items,
    )


def create_fhir_collection_bundle(device: DomainDevice) -> CollectionBundle:
    fhir_device = create_fhir_model_from_device(device=device)
    fhir_resource = Resource(
        fullUrl=f"https://cpm.co.uk/Device/{device.id}", resource=fhir_device
    )
    fhir_questionnaire = create_fhir_model_from_questionnaire_response(device=device)
    return CollectionBundle(
        resourceType="Bundle",
        id=str(uuid4()),
        total=1,
        link=[Link(relation="self", url=f"https://cpm.co.uk/Device/{device.id}")],
        entry=[fhir_resource, fhir_questionnaire],
    )


def create_fhir_searchset_bundle(
    devices: List[DomainDevice], device_type
) -> SearchsetBundle:
    entries = []
    for device in devices:
        entries.append(create_fhir_collection_bundle(device))
    return SearchsetBundle(
        resourceType="Bundle",
        id=str(uuid4()),
        total=len(devices),
        link=[
            Link(
                relation="self",
                url=f"https://cpm.co.uk/Device?device_type={device_type.lower()}",
            )
        ],
        entry=entries,
    )
