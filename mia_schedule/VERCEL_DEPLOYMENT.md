# SUTE Schedule - Vercel Deployment Guide

## Prerequisites

- GitHub account
- Vercel account (free tier)
- Git installed locally

## Deployment Steps

### 1. Push to GitHub

```bash
cd /path/to/mia_schedule
git init
git add .
git commit -m "Initial commit: SUTE Schedule PWA"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sute-schedule.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Deploy on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Select your `sute-schedule` repository
5. Vercel will auto-detect `vercel.json` configuration
6. Click "Deploy"

**Configuration is automatic** - Vercel will:
- Install dependencies from `requirements.txt`
- Use Python 3.11 (from `runtime.txt`)
- Start the Flask app using `wsgi_app` export from `app.py`

### 3. Environment Variables (Optional)

In Vercel Dashboard → Settings → Environment Variables, you can override defaults:

```
DEBUG=false
USE_CACHE=true
CACHE_LIFETIME_HOURS=24
HOST=0.0.0.0
PORT=3000
```

These are already set in `vercel.json`, so no additional configuration needed.

### 4. Custom Domain (Optional)

In Vercel Dashboard → Settings → Domains:
1. Click "Add Domain"
2. Enter your custom domain (e.g., `sute-schedule.com`)
3. Follow DNS configuration steps

## Project Structure

```
mia_schedule/
├── app.py                 # Flask application (Vercel entry point)
├── vercel.json           # Vercel configuration
├── runtime.txt           # Python version
├── requirements.txt      # Dependencies
├── config/               # Configuration modules
├── backend/              # Business logic
├── templates/            # HTML templates
├── static/               # CSS, JS, PWA files
└── data/                 # Cached data directory
```

## Troubleshooting

### Cold Start Issues
Vercel serverless functions have 15-second startup time on first request. This is normal and happens only once per deployment.

### Build Fails
Check Vercel build logs:
1. Go to Vercel Dashboard
2. Select your project
3. Click "Deployments"
4. View build logs for errors

Common issues:
- Missing `requirements.txt` dependency
- Incorrect path in `vercel.json` (must point to `mia_schedule/app.py`)
- Python version mismatch

### Groups Data Path
Ensure `Get Groups/sute_structure.json` exists locally. The path is relative to project root.

## Local Development

```bash
cd mia_schedule
pip install -r requirements.txt
python app.py
```

App runs on `http://localhost:3000`

## Automatic Redeploy

Every push to `main` branch triggers automatic redeployment on Vercel.

```bash
git add .
git commit -m "Feature: Add schedule update"
git push origin main
```

---

**Author:** nakata27  
**Project:** SUTE Schedule - Progressive Web App  
**License:** See LICENSE file

