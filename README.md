# SUTE Schedule

University timetable app for [KNUTE](https://knute.edu.ua/) students. Fetches schedule data from the MIA portal and presents it in a clean, mobile-friendly interface with offline support.

## Features

- Browse your group's schedule week by week
- Automatic course-change detection with cache invalidation
- Bilingual UI (Ukrainian / English)
- Dark theme
- PWA — installable on Android/iOS/Desktop
- Offline viewing of cached schedules
- Vercel-ready serverless deployment

## Tech stack

- **Backend**: Python 3.11, Flask, Pydantic, BeautifulSoup4
- **Frontend**: Vanilla JS, CSS (no frameworks)
- **Deployment**: Vercel (serverless Python)

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:3000` in your browser.

## Configuration

Copy `.env.example` to `.env` and adjust as needed:

```
DEBUG=false
HOST=0.0.0.0
PORT=3000
USE_CACHE=true
CACHE_LIFETIME_HOURS=24
```

## Deployment (Vercel)

The repository is configured for Vercel out of the box. Connect the repo in the Vercel dashboard — `vercel.json` at the root handles everything.

See [`VERCEL_DEPLOYMENT.md`](VERCEL_DEPLOYMENT.md) for step-by-step instructions.

## Project structure

```
├── api/
│   └── index.py              # Vercel serverless entry point
├── backend/                  # Fetcher, parser, storage, models
├── config/                   # Settings and translations
├── data/
│   └── mia_structure.json    # Faculty/course/group data
├── frontend/                 # HTML templates and static files
├── tests/                    # Backend tests
├── app.py                    # Flask application
├── requirements.txt
├── runtime.txt
└── vercel.json
```

## Running tests

```bash
python tests/test_backend.py
```

## Author

**nakata** — [github.com/nakata27](https://github.com/nakata27)

## License

Apache License 2.0 — see [LICENSE](LICENSE)
