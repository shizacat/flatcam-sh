"""Shared setup for geometry editor tests."""

import sys
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2]
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))


class Stored:
    """Holds one widget value and answers the calls the editor tools make."""

    def __init__(self, value=None):
        self.value = value

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def isChecked(self):
        return bool(self.value)


def bare(cls, **attrs):
    """
    Builds an editor object without running its constructor.

    The constructors open cursors, widgets, and canvas callbacks. A test that
    only needs the geometry methods sets the attributes it uses.
    """
    obj = cls.__new__(cls)
    for name, value in attrs.items():
        setattr(obj, name, value)
    return obj


@pytest.fixture
def new_tool():
    """Provides the constructor bypass used by the tool tests."""
    return bare
