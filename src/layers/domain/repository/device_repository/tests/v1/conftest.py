from typing import Generator

import pytest
from domain.repository.device_repository import DeviceRepository
from domain.repository.device_repository.tests.utils import repository_fixture


@pytest.fixture
def repository(request) -> Generator[DeviceRepository, None, None]:
    yield from repository_fixture(
        is_integration_test=request.node.get_closest_marker("integration"),
        repository_class=DeviceRepository,
    )
