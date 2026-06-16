import subprocess
import shlex
import requests
import yaml
from typing import Optional

with open("config.yaml", "r", encoding="utf-8") as f:
    _CFG = yaml.safe_load(f)


PROMPT_TEMPLATE = (
    "You are a professional {source_name} ({source_code}) to {target_name} ({target_code}) translator. "
    "Your goal is to accurately convey the meaning and nuances of the original {source_name} text while adhering to {target_name} grammar, vocabulary, and cultural sensitivities. "
    "Produce only the {target_name} translation, without any additional explanations or commentary. Please translate the following {source_name} text into {target_name}:\n\n\n"
)


def build_prompt(source_name: str, source_code: str, target_name: str, target_code: str, text: str) -> str:
    header = PROMPT_TEMPLATE.format(
        source_name=source_name,
        source_code=source_code,
        target_name=target_name,
        target_code=target_code,
    )
    return header + text


def run_ollama_subprocess(model: str, prompt: str, timeout: Optional[int] = None) -> str:
    # Some Ollama CLI versions accept prompt via stdin by default, others support --stdin.
    commands = [
        ["ollama", "run", model, "--stdin"],
        ["ollama", "run", model],
    ]
    last_error = None
    for cmd in commands:
        proc = subprocess.run(cmd, input=prompt.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        if proc.returncode == 0:
            return proc.stdout.decode("utf-8", errors="replace")
        stderr_text = proc.stderr.decode("utf-8", errors="replace")
        if "unknown flag: --stdin" in stderr_text or "unknown flag --stdin" in stderr_text:
            last_error = stderr_text
            continue
        raise ConnectionError(stderr_text)
    raise ConnectionError(
        "Ollama subprocess failed: could not use --stdin and fallback invocation also failed. "
        f"Last error: {last_error}"
    )


def run_ollama_http(api_base: str, model: str, prompt: str, timeout: Optional[int] = None) -> str:
    # Minimal HTTP POST to Ollama API; expects API at api_base like http://localhost:11434
    url = api_base.rstrip("/") + f"/run/{model}"
    payload = {"prompt": prompt}
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    # Ollama HTTP response may vary; try common fields
    if isinstance(data, dict) and "output" in data:
        return data["output"]
    # Fallback to full text
    return resp.text


def translate(
    *,
    source_name: str,
    source_code: str,
    target_name: str,
    target_code: str,
    text: str,
    model: Optional[str] = None,
    timeout: Optional[int] = None,
):
    model = model or _CFG.get("model")
    timeout = timeout or _CFG.get("timeout_seconds")
    prompt = build_prompt(source_name, source_code, target_name, target_code, text)
    mode = _CFG.get("ollama_mode", "subprocess")
    if mode == "http":
        api_base = _CFG.get("api_base")
        if not api_base:
            raise ValueError("api_base must be set in config.yaml for http mode")
        return run_ollama_http(api_base, model, prompt, timeout=timeout)
    else:
        return run_ollama_subprocess(model, prompt, timeout=timeout)
