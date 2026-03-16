#!/usr/bin/env python3
"""Standalone PyInstaller builder for OneMusicInstaller.

This script only packages installer_app.py into OneMusicInstaller(.exe)
using installer/OneMusicInstaller.spec. It assumes payload already exists.
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
SPEC = INSTALLER_DIR / "OneMusicInstaller.spec"
OUT_DIR = ROOT / "dist" / "installer-program"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def find_exe() -> Path | None:
    candidates = [
        INSTALLER_DIR / "dist" / "OneMusicInstaller.exe",
        INSTALLER_DIR / "dist" / "OneMusicInstaller" / "OneMusicInstaller.exe",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="1.1.0")
    parser.add_argument("--mode", choices=["onefile", "onedir", "auto"], default="auto")
    args = parser.parse_args()

    if not PAYLOAD_DIR.exists():
        raise SystemExit("payload not found. Run installer/build_installer_program.py first.")

    if not SPEC.exists():
        raise SystemExit(f"spec file not found: {SPEC}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    for item in (INSTALLER_DIR / "build", INSTALLER_DIR / "dist"):
        if item.exists():
            shutil.rmtree(item, ignore_errors=True)

    def build(mode: str) -> None:
        run([sys.executable, "-m", "PyInstaller", "--noconfirm", f"--{mode}", str(SPEC)], cwd=INSTALLER_DIR)

    if args.mode == "auto":
        try:
            build("onefile")
        except subprocess.CalledProcessError:
            print("onefile failed, fallback to onedir")
            build("onedir")
    else:
        build(args.mode)

    built = find_exe()
    if not built:
        raise SystemExit("OneMusicInstaller executable not found after build.")

    target = OUT_DIR / f"OneMusicInstaller-{args.version}.exe"
    shutil.copy2(built, target)
    print(f"Done: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
