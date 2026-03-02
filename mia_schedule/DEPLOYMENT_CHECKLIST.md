# SUTE Schedule - Vercel Deployment Checklist

## ✅ Completed Setup

### Configuration Files Created
- [x] `vercel.json` - Vercel deployment configuration
- [x] `runtime.txt` - Python version specification (3.11)
- [x] `requirements.txt` - Updated with production dependencies
- [x] `.gitignore` - Updated to exclude unnecessary files
- [x] `VERCEL_DEPLOYMENT.md` - Detailed deployment guide

### Code Fixes Applied
- [x] Removed duplicate error handlers (404 and 500)
- [x] Removed duplicate `if __name__ == '__main__'` block
- [x] Added `wsgi_app = app` for Vercel WSGI compatibility
- [x] Updated HOST from `127.0.0.1` to `0.0.0.0`
- [x] Updated PORT from `5000` to `3000` (Vercel default)

### Templates Created
- [x] `templates/404.html` - 404 error page
- [x] `templates/500.html` - 500 error page
- [x] `templates/offline.html` - PWA offline page
- [x] `templates/index.html` - Main application page
- [x] `templates/base.html` - Base template

### Project Structure
```
mia_schedule/
├── ✅ app.py                    # Flask app with WSGI export
├── ✅ vercel.json               # Vercel config
├── ✅ runtime.txt               # Python 3.11
├── ✅ requirements.txt           # Dependencies
├── ✅ .gitignore                # Git exclusions
├── ✅ VERCEL_DEPLOYMENT.md      # Deploy guide
├── config/
│   └── settings.py              # Updated HOST/PORT
├── backend/
│   └── schedule_service.py       # Business logic
├── templates/
│   ├── 404.html                 # Error page
│   ├── 500.html                 # Error page
│   ├── index.html               # Main page
│   ├── base.html                # Base template
│   └── offline.html             # PWA offline
├── static/
│   ├── manifest.json            # PWA manifest
│   ├── sw.js                    # Service worker
│   ├── css/                     # Stylesheets
│   ├── js/                      # Frontend JS
│   └── icons/                   # PWA icons
└── data/
    └── schedules/               # Cached data
```

## 🚀 Next Steps to Deploy

### 1. Initialize Git Repository
```bash
cd /home/nakata/MIA
git init
git add .
git commit -m "Initial commit: SUTE Schedule PWA ready for Vercel"
```

### 2. Create GitHub Repository
1. Go to https://github.com/new
2. Create repository name: `sute-schedule`
3. Add remote:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/sute-schedule.git
   git branch -M main
   git push -u origin main
   ```

### 3. Deploy on Vercel
1. Visit https://vercel.com
2. Sign in with GitHub
3. Click "New Project"
4. Select `sute-schedule` repository
5. Vercel auto-detects `vercel.json` - Click "Deploy"

**Deploy takes ~2 minutes**

## 📋 Verification Checklist

After deployment, verify:

- [ ] Website loads on `https://sute-schedule.vercel.app`
- [ ] API `/api/groups` returns JSON
- [ ] API `/api/schedule/<group_id>` fetches correctly
- [ ] 404 page displays for invalid routes
- [ ] Service Worker registers (`F12 → Application → Service Workers`)
- [ ] Manifest.json valid (`F12 → Application → Manifest`)
- [ ] PWA installable (Mobile: Add to Home Screen works)
- [ ] Offline mode shows cached schedule
- [ ] Custom domain works (if configured)

## ⚙️ Environment Variables

In Vercel Dashboard → Settings → Environment Variables, defaults are:

```
DEBUG = false
USE_CACHE = true
CACHE_LIFETIME_HOURS = 24
HOST = 0.0.0.0
PORT = 3000
```

**No changes needed** - already configured in `vercel.json`

## 🔧 Troubleshooting

### Build Failed
- Check Vercel build logs in Dashboard
- Ensure `vercel.json` path points to `mia_schedule/app.py`
- Verify all dependencies in `requirements.txt` are available

### 500 Error on API
- Check that `Get Groups/sute_structure.json` exists
- Verify `config/settings.py` GROUPS_FILE path is correct
- Check Vercel function logs in Dashboard

### Service Worker Issues
- Clear browser cache (F12 → Application → Clear Storage)
- Delete Service Worker and reinstall
- Verify `manifest.json` is valid (use https://manifest-validator.appspot.com/)

### Custom Domain DNS
- Point domain to Vercel nameservers
- Wait 24-48 hours for DNS propagation
- Vercel auto-generates SSL certificate

## 📝 Important Notes

- **Cold Start**: First request takes 5-15 seconds (normal)
- **Timeout**: Functions max 30 seconds (schedule fetch should be <5s)
- **Storage**: Data persists in `/data/` during deployment
- **Logs**: View in Vercel Dashboard → Deployments → Function Logs

## 👤 Author
**nakata27**

Project: SUTE Schedule - Progressive Web App  
License: Check LICENSE file  
Repository: https://github.com/nakata27/sute-schedule

