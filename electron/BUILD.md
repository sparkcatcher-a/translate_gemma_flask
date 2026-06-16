# Building TranslateGemma Local as Electron App

This guide covers building and running the Electron-packaged version of TranslateGemma Local.

## Prerequisites

1. **Node.js 18+** — Download from https://nodejs.org/
2. **Python 3.10+** — Already installed (used by Flask backend)
3. **Ollama** — Must be installed and running separately

## Local Development (Dev Mode)

### Step 1: Install Electron dependencies

```powershell
cd electron
npm install
```

### Step 2: Run in dev mode

```powershell
npm start
```

This will:
- Start the Electron app
- Spawn Flask subprocess (using system Python)
- Load UI at http://localhost:5000 inside Electron window

**Notes:**
- Flask will inherit PATH from parent process; ensure `python` command works
- Ctrl+C in terminal terminates app and cleanup happens automatically
- Check terminal output for Flask logs

## Building a Standalone Bundle (For Distribution)

### Step 1: Install PyInstaller

```powershell
# From project root
py -3 -m pip install pyinstaller
```

### Step 2: Bundle Python + Flask

```powershell
# From project root
py -3 build/bundle_python.py
```

This creates:
- `electron/resources/python-bundle/` — Standalone Python + Flask executable

### Step 3: Build Electron app

```powershell
cd electron
npm install
npm run dist
```

This creates:
- `electron/dist/TranslateGemma-Local.exe` — Portable executable
- `electron/dist/TranslateGemma Local Setup.exe` — Installer

## Troubleshooting

### "Flask failed to start"
- Ensure Ollama is running: `ollama serve`
- Check Python PATH: `where python`
- Check Flask logs in terminal output

### "Port 5000 already in use"
- Another app is using port 5000
- Kill the process: `netstat -ano | findstr :5000` then `taskkill /PID <PID> /F`
- Or restart your machine

### Bundled app won't start
- Ensure `electron/resources/python-bundle/` exists after `bundle_python.py`
- Check electron console: Press F12 in Electron window for dev tools
- Look for Flask subprocess errors in terminal

## File Structure

```
translate_gemma_flask/
├── electron/
│   ├── main.js              # Electron main process
│   ├── package.json         # Electron + build config
│   ├── resources/
│   │   └── python-bundle/   # PyInstaller output (after build)
│   └── .gitignore
├── src/
│   ├── app_flask.py         # Flask app (shared with Electron)
│   └── gemma_client.py      # Ollama client (shared with Electron)
├── build/
│   └── bundle_python.py     # PyInstaller wrapper
├── config.yaml
├── variants.yaml
├── templates/
├── static/
└── ... (other files)
```

## Next Steps

- **Bundled app distribution**: Users install `.exe` and run it; Ollama must be pre-installed
- **Config management**: Move `config.yaml` to user data dir later (~/.translategemma/)
- **Auto-update**: Implement electron-updater for v2
- **Code signing**: Sign .exe for production distribution (v2+)
