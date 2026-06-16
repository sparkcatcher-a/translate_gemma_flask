#!/usr/bin/env python
"""
PyInstaller bundler for TranslateGemma Flask app.
Packages Python + dependencies into a standalone executable that Electron can spawn.

Usage:
  python build/bundle_python.py
  
Output:
  electron/resources/python-bundle/ (one-dir structure)
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    repo_root = Path(__file__).parent.parent
    src_dir = repo_root / "src"
    app_py = src_dir / "app_flask.py"
    output_dir = repo_root / "electron" / "resources" / "python-bundle"
    
    if not app_py.exists():
        print(f"Error: {app_py} not found")
        sys.exit(1)
    
    print(f"[PyInstaller] Bundling Flask app from {app_py}")
    print(f"[PyInstaller] Output directory: {output_dir}")
    
    # Create output directory
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    
    # Run PyInstaller
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name", "flask-app",
        "--distpath", str(output_dir),
        "--buildpath", str(repo_root / "build" / "pyinstaller"),
        "--specpath", str(repo_root / "build"),
        "--add-data", f"{src_dir}{os.pathsep}src",
        "--add-data", f"{repo_root / 'config.yaml'}{os.pathsep}.",
        "--add-data", f"{repo_root / 'variants.yaml'}{os.pathsep}.",
        "--add-data", f"{repo_root / 'templates'}{os.pathsep}templates",
        "--add-data", f"{repo_root / 'static'}{os.pathsep}static",
        str(app_py),
    ]
    
    print(f"[PyInstaller] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(repo_root))
    
    if result.returncode != 0:
        print("[PyInstaller] Error: bundling failed")
        sys.exit(1)
    
    print("[PyInstaller] Bundling complete!")
    print(f"[PyInstaller] Output at: {output_dir}")

if __name__ == "__main__":
    main()
