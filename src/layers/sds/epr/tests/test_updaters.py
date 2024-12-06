from sds.epr.updaters import (
    create_or_update_mhs_device,
    remove_erroneous_additional_interactions,
    update_message_sets,
)


def test_remove_erroneous_additional_interactions():
    _additional_interactions = remove_erroneous_additional_interactions(
        message_sets=message_sets, additional_interactions=additional_interactions
    )
    assert _additional_interactions.state() == {}


def test_update_message_sets():
    _message_sets = update_message_sets(
        message_sets=message_sets, message_set_data=message_set_data
    )
    assert _message_sets.state()


def test_create_or_update_mhs_device():
    _mhs_device = create_or_update_mhs_device()


def test_create_or_update_mhs_device_default():
    _mhs_device = create_or_update_mhs_device()
