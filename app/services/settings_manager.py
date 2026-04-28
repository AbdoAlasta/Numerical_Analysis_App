import json
from pathlib import Path
from typing import Any


class SettingsManager:
    DEFAULT_SETTINGS = {
        "appearance_mode": "light",
        "font_size": 12,
        "default_epsilon": 0.0001,
        "default_max_iter": 100,
        "default_decimal_places": 6,
        "default_nonlinear_method": "Bisection",
        "default_linear_method": "Gauss Elimination",
        "default_stop_condition": "epsilon",
        "enable_rounding": False,
        "auto_save_results": True,
        "max_history_entries": 100,
        "enable_history": True,
        "show_graph_automatically": True,
        "show_step_by_step": True,
        "include_graph_in_pdf": True,
        "include_table_in_pdf": True,
        "include_datetime_in_pdf": True,
        "pdf_paper_size": "A4",
        "pdf_export_folder": "",
        "custom_pdf_title": "Numerical Analysis Report",
        "enable_advanced_validation": True,
        "show_convergence_warnings": True,
    }

    def __init__(self, filepath: str | Path) -> None:
        self._filepath = Path(filepath)
        self._settings: dict = {}
        self.load()

    def load(self) -> dict:
        try:
            if not self._filepath.exists():
                self._settings = dict(self.DEFAULT_SETTINGS)
                self._write(self._settings)
            else:
                with open(self._filepath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._settings = self._merge_with_defaults(loaded)
        except (IOError, json.JSONDecodeError):
            self._settings = dict(self.DEFAULT_SETTINGS)
        return self._settings

    def save(self, settings: dict) -> None:
        self._settings = self._merge_with_defaults(settings)
        self._write(self._settings)

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default if default is not None else self.DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value
        self._write(self._settings)

    def reset(self) -> None:
        self._settings = dict(self.DEFAULT_SETTINGS)
        self._write(self._settings)

    def all(self) -> dict:
        return dict(self._settings)

    def _merge_with_defaults(self, loaded: dict) -> dict:
        return {**self.DEFAULT_SETTINGS, **loaded}

    def _write(self, data: dict) -> None:
        try:
            self._filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass
