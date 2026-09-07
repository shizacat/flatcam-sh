# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Добавлен запуск в режиме разработчика (`./dev.sh`): трейсы исключений и стек при segfault выводятся в терминал и в `tmp/last_trace.txt`

### Fixed

- Исправлен segfault при выборе объекта: повторный `takeWidget()` уничтожал UI свойств в PyQt6

## [0.0.0] - 2026-09-07

### Added

- Start
