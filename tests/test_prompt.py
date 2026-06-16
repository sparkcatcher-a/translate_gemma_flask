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


def test_run_ollama_subprocess_falls_back_when_stdin_flag_is_invalid(monkeypatch):
    calls = []

    def fake_run(cmd, input, stdout, stderr, timeout):
        calls.append(cmd)
        if cmd == ["ollama", "run", "translategemma:12b", "--stdin"]:
            return DummyProcess(1, b"", b"unknown flag: --stdin")
        return DummyProcess(0, b"translated text", b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_ollama_subprocess("translategemma:12b", "Hello")

    assert result == "translated text"
    assert calls[0] == ["ollama", "run", "translategemma:12b", "--stdin"]
    assert calls[1] == ["ollama", "run", "translategemma:12b"]
