"""Tests for the version line drawn on the startup splash."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from PyQt6 import QtGui, QtWidgets

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from appMain import App


@pytest.fixture(scope="module")
def qapplication() -> QtWidgets.QApplication:
    """
    Creates the Qt application the splash painter needs.

    :return: running application
    """
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _blank_splash() -> QtGui.QPixmap:
    """
    Builds a splash-sized image without a version line.

    :return: filled pixmap
    """
    pixmap = QtGui.QPixmap(636, 257)
    pixmap.fill(QtGui.QColor(4, 80, 86))
    return pixmap


def _pixels(pixmap: QtGui.QPixmap) -> bytes:
    """
    Returns the pixmap pixels in a fixed format.

    :param pixmap: image to read
    :return: raw pixel bytes
    """
    image = pixmap.toImage().convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
    pointer = image.constBits()
    pointer.setsize(image.sizeInBytes())
    return bytes(pointer)


def _draw_label(label: str) -> QtGui.QPixmap:
    """
    Draws the expected splash label at the release position.

    :param label: text the splash should show
    :return: pixmap with that label
    """
    pixmap = _blank_splash()
    painter = QtGui.QPainter(pixmap)
    painter.setPen(QtGui.QColor(243, 243, 243))
    font = QtGui.QFont(QtWidgets.QApplication.font())
    font.setPixelSize(13)
    font.setBold(False)
    painter.setFont(font)
    painter.drawText(18, 110, label)
    painter.end()
    return pixmap


@pytest.mark.parametrize(
    ("version", "version_date", "label"),
    [
        ("1.9.10", "2026-10-08", "v.1.9.10 ~ 2026"),
        ("Unstable", "2023/6/31", "v.Unstable ~ 2023"),
        ("1.0", "May 2022", "v.1.0 ~ 2022"),
        ("1.0", "", "v.1.0 ~ "),
    ],
)
def test_paint_splash_release_draws_version_and_year(
    qapplication: QtWidgets.QApplication,
    version: str,
    version_date: str,
    label: str,
) -> None:
    """Verify the splash line is the version and the year from the release date."""
    host = SimpleNamespace(version=version, version_date=version_date)
    pixmap = _blank_splash()

    App._paint_splash_release(host, pixmap)

    assert _pixels(pixmap) == _pixels(_draw_label(label))
    assert _pixels(pixmap) != _pixels(_blank_splash())


def test_paint_splash_release_leaves_a_null_pixmap_untouched(
    qapplication: QtWidgets.QApplication,
) -> None:
    """Verify a missing splash image is not painted."""
    pixmap = QtGui.QPixmap()

    App._paint_splash_release(SimpleNamespace(version="1.9.10", version_date="2026-10-08"), pixmap)

    assert pixmap.isNull()
