from event.logging.logger import setup_logger


def test_setup_logger_with_default_uuid():
    from nhs_context_logging import app_logger

    setup_logger(service_name="foo")
    foo_logger = app_logger.logger()

    setup_logger(service_name="foo")
    foo2_logger = app_logger.logger()

    assert foo_logger is not foo2_logger


def test_setup_logger_with_same_uuid():
    from nhs_context_logging import app_logger

    setup_logger(service_name="foo", uuid="bar")
    foo_logger = app_logger.logger()

    setup_logger(service_name="foo", uuid="bar")
    foo2_logger = app_logger.logger()

    assert foo_logger is foo2_logger
