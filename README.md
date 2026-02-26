# VibeGuard (MVP)

VibeGuard is the unsung hero of the vibe-coding era building the "Stripe for App-Security" – an automated security governance platform explicitly designed for Solo-Founders, Indie Hackers, and AI Code Generation tools.

This repository is a monorepo containing the Minimum Viable Product:
- `api/` - The FastAPI backend wrapper for Semgrep and Google Gemini.
- `dashboard/` - The Vite + React Web UI to visualize issues.
- `action/` - The GitHub Action script that integrates VibeGuard directly into your repositories.

## Quick Start (Dev)

### Dashboard
```bash
cd dashboard
npm install
npm run dev
```

### API Backend
```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
