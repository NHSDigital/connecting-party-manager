from domain.core.compression import pkl_dumps_gzip
from domain.core.device.v2 import Device
from domain.repository.device_repository.v2 import compress_device_fields


def test_compress_device_fields_default_is_tags(device: Device):
    device_state = device.state()
    device_with_compressed_fields = compress_device_fields(device_state)
    original_tags = device_state.pop("tags")
    compressed_tags = device_with_compressed_fields.pop("tags")
    assert device_with_compressed_fields == device_state
    assert pkl_dumps_gzip(original_tags) == compressed_tags


def test_compress_device_fields_with_other_fields(device: Device):
    fields_to_compress = ["id", "keys"]

    device_state = device.state()
    device_with_compressed_fields = compress_device_fields(
        device_state, fields_to_compress=fields_to_compress
    )

    for field in fields_to_compress + ["tags"]:
        original_value = device_state.pop(field)
        compressed_value = device_with_compressed_fields.pop(field)
        assert pkl_dumps_gzip(original_value) == compressed_value
    assert device_with_compressed_fields == device_state
