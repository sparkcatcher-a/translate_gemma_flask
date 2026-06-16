import subprocess
import shlex
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


# HTTP mode removed for offline-only operation. Use subprocess-mode with local Ollama CLI.


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
    # Force subprocess mode for offline use
    return run_ollama_subprocess(model, prompt, timeout=timeout)
