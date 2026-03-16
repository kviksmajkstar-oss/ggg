#!/usr/bin/env python3
"""OneMusic AI Installer Program.

GUI installer (Tkinter) that installs bundled OneMusic files to a target directory,
creates a launcher script, and (on Windows) optionally creates desktop/start-menu
shortcuts through PowerShell.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "OneMusic AI"
DEFAULT_INSTALL_DIR_WINDOWS = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / APP_NAME
DEFAULT_INSTALL_DIR_OTHER = Path.home() / APP_NAME.replace(" ", "")


def resource_root() -> Path:
    # Works for normal run and PyInstaller onefile extraction.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


class InstallerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} Installer")
        self.geometry("680x420")
        self.resizable(False, False)

        self.src_dir = resource_root() / "payload"
        default_dir = DEFAULT_INSTALL_DIR_WINDOWS if os.name == "nt" else DEFAULT_INSTALL_DIR_OTHER
        self.install_dir_var = tk.StringVar(value=str(default_dir))
        self.create_shortcuts_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Установка {APP_NAME}", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text=(
                "Этот мастер скопирует приложение в выбранную папку и создаст лаунчер.\n"
                "Поддерживается тихий перенос файлов и создание ярлыков на Windows."
            ),
        ).pack(anchor="w", pady=(6, 18))

        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(0, 10))
        ttk.Label(row, text="Папка установки:").pack(side="left")

        path_entry = ttk.Entry(row, textvariable=self.install_dir_var, width=62)
        path_entry.pack(side="left", padx=(12, 8), fill="x", expand=True)

        ttk.Button(row, text="Выбрать", command=self.pick_install_dir).pack(side="left")

        ttk.Checkbutton(
            frame,
            text="Создать ярлыки (Desktop + Start Menu на Windows)",
            variable=self.create_shortcuts_var,
        ).pack(anchor="w", pady=(0, 14))

        self.progress = ttk.Progressbar(frame, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(8, 12))

        self.log = tk.Text(frame, height=12, state="disabled", bg="#0f172a", fg="#e2e8f0")
        self.log.pack(fill="both", expand=True)

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Установить", command=self.install).pack(side="right")
        ttk.Button(actions, text="Выход", command=self.destroy).pack(side="right", padx=(0, 8))

    def pick_install_dir(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.install_dir_var.get() or str(Path.home()))
        if selected:
            self.install_dir_var.set(selected)

    def write_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        self.update_idletasks()

    def install(self) -> None:
        target = Path(self.install_dir_var.get()).expanduser().resolve()
        if not self.src_dir.exists():
            messagebox.showerror("Ошибка", f"Не найдена папка payload: {self.src_dir}")
            return

        try:
            self.progress["value"] = 5
            self.write_log(f"Подготовка установки в: {target}")
            target.mkdir(parents=True, exist_ok=True)

            self.progress["value"] = 15
            self.copy_payload(self.src_dir, target)

            self.progress["value"] = 80
            launcher = self.create_launcher(target)
            self.write_log(f"Создан лаунчер: {launcher}")

            if self.create_shortcuts_var.get() and os.name == "nt":
                self.progress["value"] = 90
                self.create_windows_shortcuts(target, launcher)

            self.progress["value"] = 100
            self.write_log("Установка завершена успешно.")
            messagebox.showinfo("Готово", f"{APP_NAME} установлен в:\n{target}")
        except Exception as exc:  # noqa: BLE001
            self.write_log(f"Ошибка: {exc}")
            messagebox.showerror("Ошибка установки", str(exc))

    def copy_payload(self, src: Path, dst: Path) -> None:
        all_files = [p for p in src.rglob("*") if p.is_file()]
        total = max(len(all_files), 1)

        for index, source_file in enumerate(all_files, start=1):
            rel = source_file.relative_to(src)
            target_file = dst / rel
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            progress = 15 + int((index / total) * 60)
            self.progress["value"] = min(progress, 75)
            self.write_log(f"Копирование: {rel}")

    def create_launcher(self, target: Path) -> Path:
        launcher = target / ("run_onemusic.bat" if os.name == "nt" else "run_onemusic.sh")

        if os.name == "nt":
            content = (
                "@echo off\n"
                "setlocal\n"
                "cd /d %~dp0\n"
                "start \"OneMusic API\" cmd /k \"cd backend && .venv\\Scripts\\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000\"\n"
                "start \"OneMusic Frontend\" cmd /k \"cd frontend-dist && npx --yes serve -l 5173 .\"\n"
            )
        else:
            content = (
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "cd \"$(dirname \"$0\")\"\n"
                "(cd backend && .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000) &\n"
                "(cd frontend-dist && npx --yes serve -l 5173 .)\n"
            )

        launcher.write_text(content, encoding="utf-8")
        if os.name != "nt":
            launcher.chmod(0o755)
        return launcher

    def create_windows_shortcuts(self, target: Path, launcher: Path) -> None:
        desktop = Path.home() / "Desktop"
        start_menu = (
            Path(os.environ.get("APPDATA", ""))
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs"
        )
        start_menu.mkdir(parents=True, exist_ok=True)

        desktop_link = str(desktop / f"{APP_NAME}.lnk").replace('\\', '\\\\')
        start_link = str(start_menu / f"{APP_NAME}.lnk").replace('\\', '\\\\')
        launcher_path = str(launcher).replace('\\', '\\\\')

        script = (
            "$W = New-Object -ComObject WScript.Shell;"
            f"$S = $W.CreateShortcut('{desktop_link}');"
            f"$S.TargetPath = '{launcher_path}';"
            "$S.WorkingDirectory = Split-Path $S.TargetPath;"
            "$S.Save();"
            f"$S2 = $W.CreateShortcut('{start_link}');"
            f"$S2.TargetPath = '{launcher_path}';"
            "$S2.WorkingDirectory = Split-Path $S2.TargetPath;"
            "$S2.Save();"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)
        self.write_log("Ярлыки созданы.")


if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
