# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.9.1] - 2026-09-22

### Added

- Added GitHub Actions packaging for Windows, Linux, macOS Intel and macOS Apple Silicon (conda-pack; macOS ships as a DMG)
- Added a visibility eye icon in the Project tree between the object-type icon and the name (Gerber, Excellon, Geometry, CNC Job), following the light and dark tree colors

### Fixed

- Fixed a Python 3.11 SyntaxError in NCC tool add (`f-string` with a backslash) that stopped the packaged app at import
- Fixed GitHub Actions uploading the intermediate conda-pack `env.tar.gz` next to the real package; only `FlatCAM-*` archives are published
- Fixed the macOS app quitting silently when started from the read-only DMG or when Python failed: the launcher now requires a writable copy in Applications, runs `conda-unpack` for real, and shows an alert
- Fixed Linux/Windows/macOS packaging calling `python -m conda_pack`, which has no `__main__` module; the build now runs the `conda-pack` CLI
- Fixed the conda environment numpy/ortools conflict by requiring numpy 2.x, so isolation routing can import after a fresh env create
- Fixed Project tree range-selecting other layers when clicking a visibility eye while another row was already selected

## [1.9.0] - 2026-09-08

### Added

- Added a developer launch mode (`./scripts/dev.sh`) that prints exception traces and the segfault stack to the terminal and `tmp/last_trace.txt`

### Fixed

- Fixed a segfault when selecting an object: Properties UI is swapped inside a host widget instead of `QScrollArea.takeWidget()`, which destroyed the still-referenced form in PyQt6
- Fixed Tcl `cncjob` failing with KeyError `tools_mill_laser_on` on older geometry tool data

## [0.0.0] - 2026-09-07

### Added

- Start
