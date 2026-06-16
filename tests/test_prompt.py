import subprocess

from src.gemma_client import build_prompt, run_ollama_subprocess


def test_build_prompt_contains_template_parts():
    p = build_prompt('English', 'en', 'German', 'de', 'Hello')
    assert 'English (en) to German (de)' in p
    assert 'Hello' in p


class DummyProcess:
    def __init__(self, returncode: int, stdout: bytes, stderr: bytes):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_run_ollama_subprocess_uses_noninteractive_flags(monkeypatch):
    calls = []

    def fake_run(cmd, input, stdout, stderr, timeout):
        calls.append(cmd)
        if cmd == ["ollama", "run", "translategemma:12b", "--hidethinking", "--nowordwrap"]:
            return DummyProcess(1, b"", b"unknown flag")
        return DummyProcess(0, b"translated text", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_ollama_subprocess("translategemma:12b", "Hello")

    assert result == "translated text"
    assert calls[0] == ["ollama", "run", "translategemma:12b", "--hidethinking", "--nowordwrap"]
    assert calls[1] == ["ollama", "run", "translategemma:12b", "--nowordwrap"]
    assert len(calls) == 2


def test_clean_output_strips_ansi_and_normalizes_line_breaks():
    from src.gemma_client import _clean_output

    raw = "Line1\r\nLine2\x1b[31mRED\x1b[0m\rLine3"
    cleaned = _clean_output(raw)

    assert "\x1b" not in cleaned
    assert cleaned == "Line1\nLine2RED\nLine3"


def test_debug_mode_can_be_enabled_by_env(monkeypatch):
    import importlib
    import src.gemma_client as gemma_client

    monkeypatch.setenv("TRANSLATEGEMMA_DEBUG", "true")
    importlib.reload(gemma_client)

    assert gemma_client.DEBUG_MODE is True
