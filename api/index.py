"""Vercel serverless entrypoint — imports the Flask app from mia_schedule."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mia_schedule')))

from app import app  # noqa: E402  (app is the Flask application)
