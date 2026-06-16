import logging
import os
import re
import subprocess
import shlex
import yaml
from typing import Optional

logger = logging.getLogger(__name__)

with open("config.yaml", "r", encoding="utf-8") as f:
    _CFG = yaml.safe_load(f)

DEBUG_MODE = _CFG.get("debug_mode", False) or os.environ.get("TRANSLATEGEMMA_DEBUG", "").lower() in ("1", "true", "yes")
if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG)


PROMPT_TEMPLATE = (
    "You are a professional {source_name} ({source_code}) to {target_name} ({target_code}) translator. "
    "Your goal is to accurately convey the meaning and nuances of the original {source_name} text while adhering to {target_name} grammar, vocabulary, and cultural sensitivities. "
    "Produce only the {target_name} translation, without any additional explanations or commentary. Please translate the following {source_name} text into {target_name}:\n\n\n"
)


def _clean_output(text: str) -> str:
    # Strip ANSI escape sequences and normalize line endings for textarea display.
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text


def build_prompt(source_name: str, source_code: str, target_name: str, target_code: str, text: str) -> str:
    header = PROMPT_TEMPLATE.format(
        source_name=source_name,
        source_code=source_code,
        target_name=target_name,
        target_code=target_code,
    )
    return header + text


def run_ollama_subprocess(model: str, prompt: str, timeout: Optional[int] = None) -> str:
    # Run Ollama non-interactively and suppress terminal progress/thinking output.
    commands = [
        ["ollama", "run", model, "--hidethinking", "--nowordwrap"],
        ["ollama", "run", model, "--nowordwrap"],
        ["ollama", "run", model],
    ]
    last_error = None
    for cmd in commands:
        proc = subprocess.run(cmd, input=prompt.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        stdout_text = proc.stdout.decode("utf-8", errors="replace")
        stderr_text = proc.stderr.decode("utf-8", errors="replace")
        if DEBUG_MODE:
            logger.debug("Ollama cmd=%s", cmd)
            logger.debug("Prompt to model:\n%s", prompt)
            logger.debug("Ollama stdout=%r", stdout_text)
            logger.debug("Ollama stderr=%r", stderr_text)
        if proc.returncode == 0:
            return _clean_output(stdout_text)
        if "unknown flag" in stderr_text.lower():
            last_error = stderr_text
            continue
        raise ConnectionError(_clean_output(stderr_text))
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
