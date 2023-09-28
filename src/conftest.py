def pytest_collection_modifyitems(items, config):
    # add `unit` marker to all unmarked items
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker("unit")
