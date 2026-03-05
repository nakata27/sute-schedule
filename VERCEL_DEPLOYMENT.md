# SUTE Schedule — Vercel Deployment

## Prerequisites

- GitHub account
- Vercel account (free tier)
- Git installed locally

## Deployment Steps

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/nakata27/sute-schedule.git
git push -u origin main
```

If forking, update the remote URL to match your GitHub username.

### 2. Deploy on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Select your `sute-schedule` repository
5. Vercel auto-detects `vercel.json` — click "Deploy"

Vercel will:
- Install dependencies from `requirements.txt`
- Use Python 3.11 (from `runtime.txt`)
- Route all requests through `api/index.py` → Flask app

### 3. Environment Variables (Optional)

In Vercel Dashboard → Settings → Environment Variables, you can override:

```
DEBUG=false
USE_CACHE=true
CACHE_LIFETIME_HOURS=24
HOST=0.0.0.0
PORT=3000
```

These are already set in `vercel.json`.

### 4. Custom Domain (Optional)

In Vercel Dashboard → Settings → Domains, add your domain and follow the DNS steps.

## Project Structure

```
├── api/index.py          # Vercel serverless entry point
├── app.py                # Flask application
├── vercel.json           # Vercel configuration
├── runtime.txt           # Python version (3.11)
├── requirements.txt      # Dependencies
├── backend/              # Business logic
├── config/               # Settings and i18n
├── frontend/             # Templates and static files
└── data/                 # Groups data
```

## Troubleshooting

**Cold start**: First request after deployment takes ~5–15 s. This is normal.

**Build fails**: Check Vercel build logs (Dashboard → Deployments). Common causes:
- Missing dependency in `requirements.txt`
- Python version mismatch

**Groups data missing**: Ensure `data/mia_structure.json` exists in the repository.

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

App runs on `http://localhost:3000`

Every push to `main` triggers automatic redeployment on Vercel.

---

**Author:** nakata27  
**License:** MIT
