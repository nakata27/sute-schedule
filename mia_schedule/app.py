"""SUTE Schedule Flask Web Application."""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import logging
import os
import requests as http_requests

from backend.schedule_service import ScheduleService
from config.settings import (
    HOST, PORT, DEBUG,
    USE_CACHE, CACHE_LIFETIME_HOURS,
    GROUPS_FILE, DEVELOPER_CONTACTS
)
from config.i18n import get_all_translations

logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

_BASE_APP_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(_BASE_APP_DIR, 'frontend', 'templates'),
            static_folder=os.path.join(_BASE_APP_DIR, 'frontend', 'static'))
app.config['SECRET_KEY'] = 'your-secret-key-here'
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


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/api/groups')
def get_groups():
    """Get faculties/courses/groups structure."""
    try:
        groups_data = load_groups_structure()
        return jsonify({
            'success': True,
            'data': groups_data
        })
    except Exception as e:
        logger.error(f"Error in /api/groups: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
                'error': 'Missing required parameters'
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
            return jsonify({
                'success': False,
                'error': 'Failed to fetch schedule'
            }), 404

        return jsonify({
            'success': True,
            'data': schedule.model_dump(mode='json')
        })

    except Exception as e:
        logger.error(f"Error in /api/schedule/{group_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/translations/<lang>')
def get_translations(lang):
    """Get translations for language."""
    try:
        translations = get_all_translations(lang)
        return jsonify({
            'success': True,
            'data': translations
        })
    except Exception as e:
        logger.error(f"Error in /api/translations/{lang}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/announcement')
def get_announcement():
    """Proxy announcement request to upstream MIA server."""
    r1 = request.args.get('r1', '')
    try:
        resp = http_requests.get(
            'https://mia1.knute.edu.ua/time-table/show-ads',
            params={'r1': r1},
            timeout=10
        )
        resp.raise_for_status()
        return jsonify({
            'success': True,
            'html': resp.text
        })
    except Exception as e:
        logger.error(f"Error in /api/announcement: {e}")
        return jsonify({'error': 'Failed to load announcement'}), 500


@app.route('/api/contacts')
def get_contacts():
    """Get developer contacts."""
    return jsonify({
        'success': True,
        'data': DEVELOPER_CONTACTS
    })


@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest."""
    return app.send_static_file('manifest.json')


@app.route('/sw.js')
def service_worker():
    """Serve service worker."""
    response = app.send_static_file('sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response


@app.route('/offline')
def offline():
    """Offline page."""
    return render_template('offline.html')


@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    logger.error(f"Internal error: {error}")
    return render_template('500.html'), 500


wsgi_app = app


if __name__ == '__main__':
    logger.info(f"Starting SUTE Schedule App on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Cache enabled: {USE_CACHE}")

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )



