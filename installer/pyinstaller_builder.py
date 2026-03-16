#!/usr/bin/env python3
"""Standalone PyInstaller builder for OneMusicInstaller.

Can build onefile exe directly from existing payload or prepare payload from scratch.
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
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"
BACKEND_DIR = ROOT / "backend"
BUILD_LOG = INSTALLER_DIR / "pyinstaller-build.log"


def run(cmd: list[str], cwd: Path | None = None, log_file: Path | None = None) -> None:
    print("+", " ".join(cmd))
    if log_file is None:
        subprocess.run(cmd, cwd=cwd, check=True)
        return

    with log_file.open("a", encoding="utf-8") as log:
        log.write(f"\n$ {' '.join(cmd)}\n")
        subprocess.run(cmd, cwd=cwd, check=True, stdout=log, stderr=log)


def copy_backend_trimmed(src: Path, dst: Path) -> None:
    shutil.copytree(
        src,
        dst,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".venv", "__pycache__", ".pytest_cache", "*.pyc"),
    )


def prepare_payload(skip_frontend_build: bool) -> None:
    if PAYLOAD_DIR.exists():
        shutil.rmtree(PAYLOAD_DIR, ignore_errors=True)

    PAYLOAD_DIR.mkdir(parents=True, exist_ok=True)

    if not skip_frontend_build:
        run(["npm", "install"], cwd=FRONTEND_DIR)
        run(["npm", "run", "build"], cwd=FRONTEND_DIR)
    elif not FRONTEND_DIST.exists():
        raise SystemExit("frontend/dist not found. Remove --skip-frontend-build or build frontend first.")

    copy_backend_trimmed(BACKEND_DIR, PAYLOAD_DIR / "backend")
    shutil.copytree(FRONTEND_DIST, PAYLOAD_DIR / "frontend-dist", dirs_exist_ok=True)
    shutil.copy2(ROOT / "README.md", PAYLOAD_DIR / "README.md")


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
    parser.add_argument("--version", default="1.1.1")
    parser.add_argument("--mode", choices=["onefile", "onedir", "auto"], default="onefile")
    parser.add_argument("--from-scratch", action="store_true", help="prepare payload before PyInstaller build")
    parser.add_argument("--skip-frontend-build", action="store_true", help="only valid with --from-scratch")
    args = parser.parse_args()

    if args.from_scratch:
        prepare_payload(skip_frontend_build=args.skip_frontend_build)
    elif not PAYLOAD_DIR.exists():
        raise SystemExit("payload not found. Use --from-scratch or run installer/build_installer_program.py first.")

    if not SPEC.exists():
        raise SystemExit(f"spec file not found: {SPEC}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    for item in (INSTALLER_DIR / "build", INSTALLER_DIR / "dist"):
        if item.exists():
            shutil.rmtree(item, ignore_errors=True)

    if BUILD_LOG.exists():
        BUILD_LOG.unlink()

    def build(mode: str) -> None:
        run(
            [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", f"--{mode}", str(SPEC)],
            cwd=INSTALLER_DIR,
            log_file=BUILD_LOG,
        )

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
        raise SystemExit(f"OneMusicInstaller executable not found after build. See log: {BUILD_LOG}")

    target = OUT_DIR / f"OneMusicInstaller-{args.version}.exe"
    shutil.copy2(built, target)
    print(f"Done: {target}")
    print(f"Build log: {BUILD_LOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
