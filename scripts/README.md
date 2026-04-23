# Scripts

## Start public API

Use `start-public-api.ps1` to:

- start the FastAPI app on port `8000` if it is not already running
- start `ngrok` if no tunnel is active
- wait for both services to become reachable
- update `.env` with the active `VOICE_PUBLIC_BASE_URL`

Run it from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-public-api.ps1
```

Prerequisites:

- Python 3.11+ or a repo-local `.venv`
- project dependencies installed
- `ngrok` authenticated once with:

```powershell
ngrok config add-authtoken YOUR_NGROK_TOKEN
```

The scripts first look for a bundled `ngrok.exe` in the repo root, then fall back to `NGROK_PATH`, then to `ngrok` on `PATH`.
