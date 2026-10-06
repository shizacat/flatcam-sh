"""Tests for application command-line parsing."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flatcam import parse_command_line


def test_parse_command_line_reads_options_and_files() -> None:
    """Verify the startup options and the files to open are returned together."""
    parsed = parse_command_line(["--headless=1", "--shellfile=a.tcl", "--shellvar=1,2", "proj.FlatPrj"])

    assert parsed.headless == 1
    assert parsed.shellfile == "a.tcl"
    assert parsed.shellvar == "1,2"
    assert parsed.args == ["proj.FlatPrj"]


def test_parse_command_line_keeps_flags_after_a_file_as_files() -> None:
    """Verify arguments after the first file stay in the file list."""
    parsed = parse_command_line(["proj.FlatPrj", "-q", "--tb=short"])

    assert parsed.headless is None
    assert parsed.args == ["proj.FlatPrj", "-q", "--tb=short"]


def test_parse_command_line_drops_the_end_of_options_marker() -> None:
    """Verify a leading -- is not treated as a file name."""
    parsed = parse_command_line(["--", "file.gbr"])

    assert parsed.args == ["file.gbr"]


def test_parse_command_line_ignores_an_unknown_headless_name() -> None:
    """Verify an unknown headless value leaves headless unset."""
    parsed = parse_command_line(["--headless=true"])

    assert parsed.headless is None


def test_parse_command_line_ignores_the_multiprocessing_flag() -> None:
    """Verify the pool flag is accepted and does not become a file to open."""
    parsed = parse_command_line(["--multiprocessing-fork", "99", "left"])

    assert parsed.args == ["left"]
    assert parsed.headless is None


def test_parse_command_line_help_exits(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify -h prints usage and exits successfully."""
    with pytest.raises(SystemExit) as caught:
        parse_command_line(["-h"])

    assert caught.value.code == 0
    help_text = capsys.readouterr().out
    assert "Tcl script to run at startup" in help_text
    assert "shellvar_0" in help_text
    assert "without showing the main window" in help_text
    assert "files to open" in help_text
    assert "cmd_line_shellfile" not in help_text


def test_parse_command_line_rejects_an_unknown_option() -> None:
    """Verify an unknown option exits with a usage error."""
    with pytest.raises(SystemExit) as caught:
        parse_command_line(["--unknown"])

    assert caught.value.code == 2
