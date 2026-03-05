# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-03-02

### Added

- Automatic course tracking system that detects when student changes course
- Course change callback mechanism for custom handling of course changes
- `track_student_course()` method to monitor course changes
- `get_student_course()` method to retrieve current tracked course
- Automatic cache invalidation when course changes detected
- Comprehensive logging with ISO 8601 timestamps
- Full type annotations for all methods
- Multi-language support (Ukrainian and English)
- REST API endpoints for schedule retrieval
- Smart caching system with configurable lifetime
- HTML parser for schedule data extraction
- Multiple storage backends (JSON and SQLite)

### Features

- Automatic Schedule Tracking: Monitors and updates schedules on course changes
- Smart Caching: Configurable cache with automatic invalidation
- Multi-language Support: Full support for Ukrainian and English interfaces
- REST API: Complete API for schedule management
- Real-time Updates: Automatic schedule updates on course changes

## Technical Details

- Developed with Python 3.8+
- Flask web framework
- Pydantic for data validation
- Support for both JSON and SQLite storage
- Comprehensive logging system
- Type-safe codebase with full type hints

