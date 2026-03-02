# SUTE Schedule

Dynamic university schedule management system with automatic course tracking and intelligent caching.

## Features

- **Automatic Course Tracking**: Automatically detects course changes and refreshes schedules
- **Smart Caching**: Configurable cache with automatic invalidation on course changes
- **Multi-language Support**: English and Ukrainian interface
- **REST API**: Complete API for schedule retrieval and management
- **Real-time Updates**: Automatic schedule updates when course information changes

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from backend.schedule_service import ScheduleService

def on_course_changed(group_id, old_course, new_course):
    print(f"Course changed: {old_course} -> {new_course}")

service = ScheduleService(course_change_callback=on_course_changed)

schedule = service.get_schedule(
    group_id="3705",
    faculty_id="1",
    course="2",
    group_name="PZ-31m",
    faculty_name="FPMT"
)
```

## Running the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## Configuration

Set environment variables:

- `DEBUG`: Enable debug mode (default: False)
- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 5000)
- `USE_CACHE`: Enable caching (default: True)
- `CACHE_LIFETIME_HOURS`: Cache lifetime in hours (default: 24)

## API Endpoints

- `GET /api/groups` - Get faculties/courses/groups structure
- `GET /api/schedule/<group_id>` - Get schedule for group
- `GET /api/translations/<lang>` - Get translations
- `GET /api/contacts` - Get developer contacts

## Architecture

```
backend/
├── fetcher/          Schedule data fetching
├── parser/           HTML parsing
├── storage/          JSON/SQLite storage
├── models/           Pydantic data models
└── schedule_service.py   Main service with course tracking

frontend/
├── static/           CSS, JavaScript, images
└── templates/        HTML templates

config/
├── settings.py       Application configuration
└── i18n.py          Localization and translations
```

## Requirements

- Python 3.8+
- Flask
- Pydantic
- Requests

## Author

[@nakata27](https://github.com/nakata27)

## License

MIT License

