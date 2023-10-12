from uuid import uuid4

from nhs_context_logging import app_logger


def setup_logger(service_name: str, uuid: str = None):
    if uuid is None:
        uuid = str(uuid4())
    app_logger._is_setup = False
    app_logger.setup(service_name="-".join((service_name, uuid)))
