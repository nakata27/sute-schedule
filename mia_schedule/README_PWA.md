# SUTE Schedule 📱

Progressive Web App for dynamic university schedule management with automatic course tracking and offline support.

## ✨ Features

- **📱 Progressive Web App**: Install on any device (Android, iOS, Desktop)
- **🔄 Automatic Course Tracking**: Detects course changes and refreshes schedules automatically
- **💾 Smart Caching**: Configurable cache with automatic invalidation
- **📡 Offline Support**: View cached schedules without internet connection
- **🌍 Multi-language**: Ukrainian and English interface
- **🎨 Dark Theme**: Modern dark luxury theme inspired by Apple/Telegram
- **⚡ Fast & Lightweight**: Optimized performance with service workers
- **🔔 Background Sync**: Automatic schedule updates when connection restored

## 🚀 Quick Start

### Installation

```bash
cd mia_schedule
python3 -m venv venv
source venv/bin/activate.fish
pip install -r requirements.txt
```

### Running

```bash
python app.py
```

Open: `http://127.0.0.1:5000`

## 📱 PWA Installation

### Desktop (Chrome, Edge, Brave)
1. Open app in browser
2. Click install icon (➕) in address bar
3. Click "Install"
4. App added to desktop

### Android
1. Open in Chrome
2. Tap menu (⋮) → "Add to Home screen"
3. Or accept install banner
4. Icon added to home screen

### iOS (Safari)
1. Open in Safari
2. Tap Share (□↑)
3. "Add to Home Screen"
4. Tap "Add"

## 📡 Offline Capabilities

**Works offline:**
- ✅ View cached schedules
- ✅ Browse schedule data
- ✅ All UI features
- ✅ Switch weeks (if cached)

**Requires internet:**
- ❌ Load new schedules
- ❌ Refresh data
- ❌ Change group

**Background Sync:**
- Auto-syncs when online
- Updates cached data

## 🏗️ Architecture

```
sute-schedule/
├── static/
│   ├── manifest.json    # PWA manifest
│   ├── sw.js           # Service Worker
│   ├── icons/          # PWA icons
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html       # PWA setup
│   ├── index.html
│   └── offline.html    # Offline page
├── backend/
│   ├── schedule_service.py
│   ├── fetcher/
│   ├── parser/
│   ├── storage/
│   └── models/
├── config/
│   ├── settings.py
│   └── i18n.py
└── app.py
```

## 🎯 Configuration

```bash
DEBUG=False
HOST=127.0.0.1
PORT=5000
USE_CACHE=True
CACHE_LIFETIME_HOURS=24
```

## 📊 PWA Score Target

- Performance: 90+
- Accessibility: 90+
- Best Practices: 90+
- SEO: 90+
- PWA: 90+

## 🔧 Development

### Generate Icons

```bash
python generate_icons.py
```

### Service Worker Updates

Increment version in `sw.js`:
```javascript
const CACHE_VERSION = 'sute-schedule-v2';
```

### Testing Offline

1. DevTools (F12) → Network
2. Select "Offline"
3. Refresh page
4. Offline page appears

## 🌐 API Endpoints

- `GET /` - Main page
- `GET /api/groups` - Groups structure
- `GET /api/schedule/<id>` - Schedule
- `GET /manifest.json` - PWA manifest
- `GET /sw.js` - Service Worker
- `GET /offline` - Offline page

## 📦 Requirements

- Python 3.8+
- Flask
- Pydantic
- Requests
- BeautifulSoup4

## 🐛 Troubleshooting

**Service Worker not registering:**
- Check console for errors
- Use HTTPS or localhost
- Clear cache

**Install prompt not showing:**
- Validate manifest.json
- Check all icons exist
- Verify service worker active

**Offline page not working:**
- Check `/offline` returns 200
- Verify SW cache includes it
- Check SW is active

## 👨‍💻 Author

[@nakata27](https://github.com/nakata27)

## 📄 License

MIT License

## 🔗 Links

- [PWA Documentation](https://web.dev/progressive-web-apps/)
- [Service Worker API](https://developer.mozilla.org/docs/Web/API/Service_Worker_API)

