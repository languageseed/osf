# OSF Deployment Guide

Deploy OSF to production using Vercel (frontend) and Railway (backend).

## Quick Start

### Prerequisites

- GitHub account
- [Vercel](https://vercel.com) account (free tier works)
- [Railway](https://railway.app) account (free tier works)
- [Google AI Studio](https://aistudio.google.com/) API key

### 1. Push to GitHub

```bash
# From osf-demo directory
git init
git add .
git commit -m "Initial OSF commit"
git remote add origin https://github.com/language-seed/osf.git
git push -u origin main
```

---

## Backend Deployment (Railway)

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub Repo"
3. Select the `osf` repository
4. Set the root directory to `projects/osf-demo/backend`

### Step 2: Add PostgreSQL

1. In your Railway project, click "New" → "Database" → "PostgreSQL"
2. Railway automatically sets `DATABASE_URL`

### Step 3: Add Redis (Optional)

1. Click "New" → "Database" → "Redis"
2. Railway automatically sets `REDIS_URL`

### Step 4: Set Environment Variables

In Railway dashboard → Variables, add:

| Variable | Value |
|----------|-------|
| `GOOGLE_API_KEY` | Your Gemini API key from AI Studio |
| `ENVIRONMENT` | `production` |
| `API_SECRET_KEY` | Generate: `openssl rand -hex 32` |
| `CORS_ORIGINS` | `https://your-app.vercel.app` |

### Step 5: Deploy

Railway auto-deploys on push. Your API will be at:
```
https://osf-api-production.up.railway.app
```

Note the URL for frontend configuration.

---

## Frontend Deployment (Vercel)

### Step 1: Import Project

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Set root directory to `projects/osf-demo/frontend`

### Step 2: Configure Build

Vercel auto-detects SvelteKit. Verify settings:

| Setting | Value |
|---------|-------|
| Framework Preset | SvelteKit |
| Build Command | `npm run build` |
| Output Directory | `.svelte-kit` |
| Install Command | `npm install` |

### Step 3: Set Environment Variables

In Vercel dashboard → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `PUBLIC_API_URL` | `https://your-railway-url.up.railway.app` |

### Step 4: Deploy

Click "Deploy". Your frontend will be at:
```
https://osf.vercel.app
```

---

## Post-Deployment

### Verify Deployment

1. **Frontend**: Visit your Vercel URL
2. **Backend Health**: `curl https://your-railway-url/health`
3. **API Docs**: `https://your-railway-url/docs`

### Update CORS

After getting your Vercel URL, update Railway:

```bash
CORS_ORIGINS=https://osf.vercel.app,https://osf-*.vercel.app
```

---

## Custom Domain (Optional)

### Vercel Custom Domain

1. Vercel Dashboard → Settings → Domains
2. Add your domain (e.g., `osf.languageseed.com`)
3. Update DNS as instructed

### Railway Custom Domain

1. Railway Dashboard → Settings → Domains
2. Add custom domain for API (e.g., `api.osf.languageseed.com`)
3. Update CORS_ORIGINS to include new domain

---

## Environment Variables Reference

### Backend (Railway)

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Gemini API key |
| `DATABASE_URL` | Auto | PostgreSQL connection (Railway provides) |
| `REDIS_URL` | Auto | Redis connection (Railway provides) |
| `ENVIRONMENT` | Yes | `production` |
| `API_SECRET_KEY` | Yes | Random secret for security |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins |
| `GEMINI_MODEL` | No | Default: `gemini-2.0-flash` |

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `PUBLIC_API_URL` | Yes | Railway backend URL |

---

## Troubleshooting

### CORS Errors

```
Access to fetch at 'https://api...' has been blocked by CORS
```

**Fix**: Add your Vercel domain to `CORS_ORIGINS` in Railway.

### API Connection Failed

```
Failed to fetch from API
```

**Check**:
1. Railway deployment is running (`/health` returns 200)
2. `PUBLIC_API_URL` is correct in Vercel
3. No trailing slash in API URL

### Build Failures

**Frontend**: Check Node version (needs 18+)
**Backend**: Check Python version (needs 3.12)

### Database Connection

If using Railway PostgreSQL, ensure `DATABASE_URL` is automatically set. Check Railway logs for connection errors.

---

## Local Development

```bash
# Terminal 1: Backend
cd backend
cp ../env.example .env
# Edit .env with your GOOGLE_API_KEY
docker compose up

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

---

## CI/CD

Both Vercel and Railway automatically deploy on push to `main`.

For staging, create a `develop` branch and configure:
- Vercel: Preview deployments are automatic
- Railway: Create separate environment for `develop` branch

---

## Monitoring

### Railway
- Logs: Railway Dashboard → Deployments → Logs
- Metrics: Railway Dashboard → Metrics

### Vercel
- Analytics: Vercel Dashboard → Analytics
- Logs: Vercel Dashboard → Functions → Logs

---

## Cost Estimates

### Free Tier Limits

| Service | Free Tier |
|---------|-----------|
| Vercel | 100GB bandwidth/month |
| Railway | $5 free credits/month |
| Gemini API | Free tier available |

### Production Estimates

For ~1000 daily users:
- Vercel Pro: ~$20/month
- Railway: ~$10-20/month
- Gemini API: Pay per use

---

*Last updated: January 2026*
