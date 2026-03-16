#!/usr/bin/env python3
"""Build OneMusicInstaller.exe via PyInstaller.

Python-native replacement for PowerShell-heavy flow.
- Prepares payload (backend/frontend-dist/README)
- Excludes heavy dirs (.venv, __pycache__, .pytest_cache, node_modules)
- Runs PyInstaller in onefile mode, then onedir fallback
- Copies final exe to dist/installer-program/OneMusicInstaller-<version>.exe
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER_DIR = ROOT / "installer"
PAYLOAD_DIR = INSTALLER_DIR / "payload"
OUT_DIR = ROOT / "dist" / "installer-program"
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"
BACKEND_DIR = ROOT / "backend"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def copy_backend_trimmed(src: Path, dst: Path) -> None:
    shutil.copytree(
        src,
        dst,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".venv", "__pycache__", ".pytest_cache", "*.pyc"),
    )
    for extra in (".venv",):
        target = dst / extra
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)


def find_built_exe() -> Path | None:
    candidates = [
        INSTALLER_DIR / "dist" / "OneMusicInstaller.exe",
        INSTALLER_DIR / "dist" / "OneMusicInstaller" / "OneMusicInstaller.exe",
        ROOT / "dist" / "OneMusicInstaller.exe",
        ROOT / "dist" / "OneMusicInstaller" / "OneMusicInstaller.exe",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def ensure_pyinstaller() -> None:
    run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_installer_exe() -> None:
    base_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--name",
        "OneMusicInstaller",
        "--add-data",
        "payload;payload",
        "installer_app.py",
    ]

    # Clean previous artifacts to avoid stale lookup.
    for p in (INSTALLER_DIR / "build", INSTALLER_DIR / "dist"):
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)

    try:
        run(base_cmd[:3] + ["--onefile"] + base_cmd[3:], cwd=INSTALLER_DIR)
    except subprocess.CalledProcessError:
        print("onefile build failed, retrying with --onedir...")
        run(base_cmd[:3] + ["--onedir"] + base_cmd[3:], cwd=INSTALLER_DIR)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="1.0.8")
    parser.add_argument("--skip-frontend-build", action="store_true")
    args = parser.parse_args()

    if PAYLOAD_DIR.exists():
        shutil.rmtree(PAYLOAD_DIR, ignore_errors=True)
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR, ignore_errors=True)
    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not args.skip_frontend_build:
        run(["npm", "install"], cwd=FRONTEND_DIR)
        run(["npm", "run", "build"], cwd=FRONTEND_DIR)
    elif not FRONTEND_DIST.exists():
        raise SystemExit("frontend/dist not found. Remove --skip-frontend-build or build frontend first.")

    copy_backend_trimmed(BACKEND_DIR, PAYLOAD_DIR / "backend")
    shutil.copytree(FRONTEND_DIST, PAYLOAD_DIR / "frontend-dist", dirs_exist_ok=True)
    shutil.copy2(ROOT / "README.md", PAYLOAD_DIR / "README.md")

    ensure_pyinstaller()
    build_installer_exe()

    built = find_built_exe()
    if not built:
        raise SystemExit("Installer binary not found after PyInstaller build.")

    final_exe = OUT_DIR / f"OneMusicInstaller-{args.version}.exe"
    shutil.copy2(built, final_exe)
    print(f"Done: {final_exe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
