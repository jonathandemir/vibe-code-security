# Vouch (MVP)

[![Vouch Score](https://vouch-api.onrender.com/badge/vouch)](https://vouch-secure.com)
Vouch for your code. AI-Native Security in 300 seconds. Vouch is the "Stripe for App-Security" for the Vibe-Coding era – an automated security governance platform explicitly designed for Solo-Founders, Indie Hackers, and AI Code Generation tools.

This repository is a monorepo containing the Minimum Viable Product:
- `api/` - The FastAPI backend wrapper for Semgrep and Google Gemini.
- `dashboard/` - The Vite + React Web UI to visualize issues.

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
