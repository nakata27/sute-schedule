"""Vercel serverless entry point for SUTE Schedule API."""

import sys
import os

# Add project root to sys.path so 'backend' package is importable.
# On Vercel, only the directory of this file (/var/task/api/) is in sys.path by default.
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

import json
import logging

from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.schedule_service import ScheduleService
from backend.config.settings import (
    DEBUG, USE_CACHE, CACHE_LIFETIME_HOURS,
    GROUPS_FILE, DEVELOPER_CONTACTS
)
from backend.config.i18n import get_all_translations

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sute-schedule-secret')
CORS(app)

schedule_service = ScheduleService(
    use_cache=USE_CACHE,
    cache_lifetime_hours=CACHE_LIFETIME_HOURS
)


def load_groups_structure():
    """Load groups structure from JSON."""
    try:
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading groups structure: {e}")
        return []


@app.route('/api/groups')
def get_groups():
    """Get faculties/courses/groups structure."""
    try:
        groups_data = load_groups_structure()
        return jsonify({'success': True, 'data': groups_data})
    except Exception as e:
        logger.error(f"Error in /api/groups: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/schedule/<group_id>')
def get_schedule(group_id):
    """Get schedule for a group."""
    try:
        faculty_id = request.args.get('faculty_id')
        faculty_name = request.args.get('faculty_name')
        course = request.args.get('course')
        group_name = request.args.get('group_name')
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'

        if not all([faculty_id, faculty_name, course, group_name]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: faculty_id, faculty_name, course, group_name'
            }), 400

        schedule = schedule_service.get_schedule(
            group_id=group_id,
            faculty_id=faculty_id,
            course=course,
            group_name=group_name,
            faculty_name=faculty_name,
            force_refresh=force_refresh
        )

        if not schedule:
            return jsonify({'success': False, 'error': 'Failed to fetch schedule'}), 404

        return jsonify({'success': True, 'data': schedule.model_dump(mode='json')})

    except Exception as e:
        logger.error(f"Error in /api/schedule/{group_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/translations/<lang>')
def get_translations(lang):
    """Get translations for language."""
    try:
        translations = get_all_translations(lang)
        return jsonify({'success': True, 'data': translations})
    except Exception as e:
        logger.error(f"Error in /api/translations/{lang}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/contacts')
def get_contacts():
    """Get developer contacts."""
    return jsonify({'success': True, 'data': DEVELOPER_CONTACTS})
