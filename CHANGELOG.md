# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.9.0] - 2026-09-08

### Added

- Added a developer launch mode (`./scripts/dev.sh`) that prints exception traces and the segfault stack to the terminal and `tmp/last_trace.txt`

### Fixed

- Fixed a segfault when selecting an object: Properties UI is swapped inside a host widget instead of `QScrollArea.takeWidget()`, which destroyed the still-referenced form in PyQt6
- Fixed Tcl `cncjob` failing with KeyError `tools_mill_laser_on` on older geometry tool data

## [0.0.0] - 2026-09-07

### Added

- Start
