# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added a developer launch mode (`./dev.sh`) that prints exception traces and the segfault stack to the terminal and `tmp/last_trace.txt`

### Fixed

- Fixed a segfault when selecting an object: a second discarded `takeWidget()` destroyed the Properties UI in PyQt6

## [0.0.0] - 2026-09-07

### Added

- Start
