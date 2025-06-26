import pytest

# Ignore return values for certain CLI style tests

def pytest_pyfunc_call(pyfuncitem):
    if pyfuncitem.name in {"test_roll_api", "test_multiple_rolls"}:
        pyfuncitem.obj()
        return True
