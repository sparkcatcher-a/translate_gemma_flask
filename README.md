# TranslateGemma Local (Flask)

Simple local desktop-style translator UI using Ollama's TranslateGemma models.

## Prerequisites

1. Install Python 3.14 or later.
2. Install Ollama separately, then pull a model to use locally.
   - Example: `ollama pull translategemma:12b`
   - See Ollama setup docs: https://ollama.com/docs
3. Ensure Ollama is available either via subprocess or HTTP API.

## Setup

Open a terminal in the project folder and run:

```powershell
cd /d D:\Libraries\Code\translate_gemma_flask
py -3.14 -m pip install --upgrade pip setuptools wheel
py -3.14 -m pip install -r requirements.txt
```

> If you do not have `py -3.14`, install Python 3.14 and use the appropriate launcher or full path to that interpreter.

## Run the app

```powershell
py -3.14 src/app_flask.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Run tests

```powershell
py -3.14 -m pytest -q
```

## Configuration

The app reads `config.yaml` for defaults:

- `model` — default Ollama model, e.g. `translategemma:12b`
- `default_source` — default source language code, e.g. `en`
- `default_target` — default target language code, e.g. `de`
- `ollama_mode` — `subprocess` or `http`
- `api_base` — Ollama HTTP base URL when using `http` mode
- `timeout_seconds` — request timeout in seconds

## Notes

- If you use `ollama serve`, set `ollama_mode: http` and configure `api_base` in `config.yaml`.
- The UI is intentionally simple and made for manual translation requests rather than live editing.

## Updating the offline variants list

This project uses an offline `variants.yaml` file (at the project root) containing the full set of base languages and their variants supported by TranslateGemma. To refresh that file from the official source (run this when you update your local TranslateGemma model), do the following on a machine with internet access:

1. (Optional but recommended) Create and activate a virtualenv:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install the single temporary dependency and run the generator script:

```powershell
py -3 -m pip install requests PyYAML
py -3 scripts\generate_variants.py
```

This will overwrite `variants.yaml` with the canonical list fetched from the TranslateGemma page. After this step you can remove the temporary `requests` package from the environment if you like.

Notes:
- The generator script is `scripts/generate_variants.py`. It is intended for manual use only.
- If you prefer not to keep network-capable scripts, you can delete the `scripts/` folder after updating `variants.yaml`.

## Credit

- Parts of the prompt and client logic were inspired by `arrase/gemma-translator`. 
