"""
Numerical Analysis Calculator
Entry point — bootstraps services, applies theme, and starts the GUI.
Run with:  python main.py
"""
import sys
import tkinter as tk
from pathlib import Path


def main() -> None:
    # ── Resolve project root and data paths ──────────────────────────
    root_dir = Path(__file__).parent.resolve()
    data_dir  = root_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    settings_file = data_dir / "settings.json"
    history_file  = data_dir / "history.json"

    # ── Services (no GUI dependency) ─────────────────────────────────
    from app.services.settings_manager import SettingsManager
    from app.services.history_manager  import HistoryManager

    sm = SettingsManager(settings_file)
    hm = HistoryManager(history_file,
                        max_entries=sm.get("max_history_entries", 100))

    # ── Apply CTk appearance before any window is created ────────────
    import customtkinter as ctk
    mode = sm.get("appearance_mode", "light")
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme("blue")

    # ── Launch main window ────────────────────────────────────────────
    from app.gui.main_window import MainWindow
    app = MainWindow(sm, hm)
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Last-resort error dialog if the window never opened
        try:
            import tkinter.messagebox as mb
            mb.showerror("Startup Error",
                         f"Failed to start Numerical Analysis Calculator:\n\n{exc}")
        except Exception:
            print(f"Fatal startup error: {exc}", file=sys.stderr)
        sys.exit(1)
