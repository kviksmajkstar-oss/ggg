#!/usr/bin/env python3
"""Install/upgrade PyInstaller with basic diagnostics."""

from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str]) -> None:
    print('+', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    print(f'Python: {sys.executable}')
    run([sys.executable, '-m', 'pip', '--version'])
    run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pyinstaller'])
    run([sys.executable, '-m', 'PyInstaller', '--version'])
    print('PyInstaller installed successfully.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
