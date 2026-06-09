# tests/conftest.py
from pathlib import Path

def pytest_collection_modifyitems(session, config, items):
    """
    Sorts tests using pathlib to prevent any OS path mismatch errors.
    """
    if not items:
        return

    def get_test_priority(item):
        # item.path is a native pathlib.Path object in modern pytest
        # (Fall back to Path(item.fspath) for older versions)
        test_path = getattr(item, 'path', Path(item.fspath))

        # Check the folder names safely as sequence parts
        path_parts = test_path.parts

        if "unit" in path_parts:
            return 0  # Highest priority
        elif "integration" in path_parts:
            return 1  # Medium priority
        else:
            return 2  # Lowest priority

    # Sort and update the list using PyCharm-safe slice assignment
    items[:] = sorted(items, key=get_test_priority)
