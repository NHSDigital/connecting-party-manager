from pathlib import Path
from typing import Set
from uuid import uuid4

from nhs_context_logging import app_logger


def setup_logger(service_name: str, uuid: str = None, redacted_fields: Set[str] = None):
    service_name = Path(service_name).parent.stem
    if uuid is None:
        uuid = str(uuid4())
    app_logger._is_setup = False
    app_logger.setup(
        service_name="-".join((service_name, uuid)),
        config_kwargs={"prepend_module_name": True},
        redact_fields=redacted_fields,
    )
