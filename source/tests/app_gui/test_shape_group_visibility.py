"""Tests for hiding a shape group on the canvas."""

import sys
from pathlib import Path

from shapely import LineString

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from appGUI.VisPyVisuals import ShapeCollectionVisual, ShapeGroup


def _collection_with_line() -> tuple[ShapeCollectionVisual, ShapeGroup, int, dict]:
    """Builds one collection, one group, and a line, and records the next canvas rebuild."""
    collection = ShapeCollectionVisual(linewidth=1, layers=1, pool=None, fcoptions={})
    group = ShapeGroup(collection)
    key = group.add(shape=LineString([(0, 0), (1, 0)]), color="#000000FF", layer=0, update=False)
    seen = {}

    def rebuild() -> None:
        seen["dirty"] = collection._dirty
        seen["visible"] = collection.data[key]["visible"]

    collection._ShapeCollectionVisual__update = rebuild
    collection._dirty = False
    return collection, group, key, seen


def test_hiding_a_group_rebuilds_the_canvas() -> None:
    """Verify hiding a group marks the collection dirty and drops the shape from the frame."""
    _collection, group, _key, seen = _collection_with_line()

    group.visible = False

    assert seen == {"dirty": True, "visible": False}


def test_showing_a_group_again_rebuilds_the_canvas() -> None:
    """Verify showing a group again marks the collection dirty and includes the shape."""
    _collection, group, _key, seen = _collection_with_line()
    group.visible = False
    seen.clear()
    group._collection._dirty = False

    group.visible = True

    assert seen == {"dirty": True, "visible": True}


def test_update_visibility_rebuilds_the_canvas() -> None:
    """Verify a partial visibility change also forces a canvas rebuild."""
    _collection, group, key, seen = _collection_with_line()

    group.update_visibility(False, indexes=[key])

    assert seen == {"dirty": True, "visible": False}
