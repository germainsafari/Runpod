# Deploy Flux Studio (Frontend + Backend)

This guide covers deploying the chat UI and API proxy separately:

| Component | Best platform | Why |
|-----------|---------------|-----|
| **Backend** (`app/backend`) | **Render** | FastAPI needs a long-lived server; status polling stays under request timeouts |
| **Frontend** (`app/frontend`) | **Vercel** or **Render Static Site** | Static React build; cheap and fast CDN |

> **Note:** Vercel Serverless Functions are **not** ideal for the backend here because image jobs can run 30–120 seconds and the `/api/chat` sync endpoint polls for up to 9 minutes.

---

## Architecture after deploy

```
Browser (Vercel)
    → VITE_API_BASE_URL
        → Render FastAPI (/api/chat/submit + /api/chat/status)
            → RunPod Serverless (flux-studio-v2)
```

---

## Part 1 — Deploy backend on Render

### Option A: Blueprint (recommended)

1. Push this repo to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**.
3. Connect the repo; Render reads `render.yaml` at the root.
4. Set secret env vars when prompted:
   - `RUNPOD_API_KEY` — from [RunPod Settings](https://www.runpod.io/console/user/settings)
   - `RUNPOD_ENDPOINT_ID` — e.g. `7n4p3czd3nphae` (flux-studio-v2)
   - `FRONTEND_URL` — add after frontend deploy, e.g. `https://flux-studio.vercel.app`
5. Deploy. Note the URL: `https://flux-studio-api.onrender.com`

### Option B: Manual Web Service

| Setting | Value |
|---------|-------|
| Root Directory | `app/backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/api/health` |

**Environment variables**

```
RUNPOD_API_KEY=rpa_...
RUNPOD_ENDPOINT_ID=7n4p3czd3nphae
FRONTEND_URL=https://your-frontend.vercel.app
```

Verify:

```bash
curl https://flux-studio-api.onrender.com/api/health
```

Expected:

```json
{"status":"ok","endpoint_configured":true,"api_key_configured":true,"endpoint_id":"7n4p3czd3nphae"}
```

---

## Part 2 — Deploy frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project** → import GitHub repo.
2. Configure:

| Setting | Value |
|---------|-------|
| Framework Preset | Vite |
| Root Directory | `app/frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

3. **Environment variable** (Production):

```
VITE_API_BASE_URL=https://flux-studio-api.onrender.com
```

No trailing slash. Redeploy after changing this.

**Important:** In Vercel project settings, set **Root Directory** to `app/frontend`. Do **not** use a build command like `cd app/frontend && ...` — Vercel is already inside that folder.

| Vercel setting | Value |
|----------------|-------|
| Root Directory | `app/frontend` |
| Build Command | `npm run build` (default) |
| Output Directory | `dist` |
| Install Command | `npm install` (default) |

4. Deploy → open `https://your-app.vercel.app`

5. Go back to Render and set `FRONTEND_URL` to your Vercel URL (for CORS). Redeploy backend.

### Alternative: Frontend on Render Static Site

1. **New Static Site** → connect repo.
2. Root: `app/frontend`
3. Build: `npm install && npm run build`
4. Publish directory: `dist`
5. Add env var `VITE_API_BASE_URL` in Render static site settings.

---

## Part 3 — Deploy both on Render only

You can host everything on Render:

1. **Web Service** — backend (see Part 1).
2. **Static Site** — frontend with `VITE_API_BASE_URL` pointing to the web service URL.

Pros: one billing account. Cons: static site CDN is fine; free web service sleeps after inactivity (~50s cold start).

---

## Local development vs production

| Mode | Frontend | API calls |
|------|----------|-----------|
| Local | `npm run dev` (port 5173) | Proxied to `localhost:8000` via Vite |
| Local full stack | Backend on 8000 serves built `dist/` | Same origin |
| Production | Vercel CDN | `VITE_API_BASE_URL` + `/api/...` |

---

## Checklist before demo/submission

- [ ] RunPod endpoint healthy (`flux-studio-v2`, worker ready)
- [ ] Backend `/api/health` returns `endpoint_configured: true`
- [ ] Frontend loads and shows **RunPod connected**
- [ ] Generate at **512×512** (Settings)
- [ ] Library shows past images
- [ ] Pin/rename/project organization works (stored in browser localStorage)

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS error in browser | Set `FRONTEND_URL` on Render to exact Vercel URL |
| `Configure API keys` in UI | Backend missing `RUNPOD_*` env vars |
| Jobs stuck / timeout | RunPod worker cold start; set `workersMin=1` on endpoint |
| 502 from backend | Render service sleeping; first request wakes it (~30–60s) |
| Blank page on Vercel | Ensure `vercel.json` rewrites SPA routes; root is `app/frontend` |

---

## Security notes

- Never commit `.env` or expose `RUNPOD_API_KEY` in the frontend.
- The backend holds secrets; the browser only talks to your API.
- Rotate keys if they were shared in chat or screenshots.
