import customtkinter as ctk
from tkinter import filedialog

from app.services.settings_manager import SettingsManager


BLUE   = "#2563EB"
PURPLE = "#7C3AED"
GREEN  = "#059669"
BG_CARD = ("white", "#1E293B")
BORDER  = ("#E2E8F0", "#334155")


class SettingsPage(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller, settings_manager: SettingsManager) -> None:
        super().__init__(parent, corner_radius=0, fg_color=("white", "#0F172A"))
        self.controller = controller
        self.sm = settings_manager
        self.grid_columnconfigure(0, weight=1)
        self._vars: dict = {}
        self._build_header()
        self._build_calculation_card()
        self._build_ui_card()
        self._build_export_card()
        self._build_history_card()
        self._build_advanced_card()
        self._build_save_row()
        self._load_values()

    # ── Header ────────────────────────────────────────────────────────
    def _build_header(self) -> None:
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=36, pady=(32, 8))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            hdr, text="Settings & Preferences",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"), anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            hdr, text="Customize the application to suit your workflow",
            font=ctk.CTkFont(size=13), text_color=("#64748B", "#94A3B8"), anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        ctk.CTkFrame(hdr, height=2, fg_color=BLUE, corner_radius=2
                     ).grid(row=2, column=0, sticky="ew", pady=(10, 0))

    # ── Card helper ───────────────────────────────────────────────────
    def _card(self, row: int, title: str, color: str = BLUE) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self, corner_radius=12, fg_color=BG_CARD,
            border_width=1, border_color=BORDER,
        )
        card.grid(row=row, column=0, sticky="ew", padx=36, pady=6)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=0
                     ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"), anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(12, 6))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
        inner.grid_columnconfigure(1, weight=1)
        return inner

    def _row(self, parent: ctk.CTkFrame, row: int, label: str,
             hint: str = "") -> int:
        ctk.CTkLabel(
            parent, text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#374151", "#CBD5E1"), anchor="w",
        ).grid(row=row, column=0, sticky="w", pady=(6, 0), padx=(0, 16))
        if hint:
            ctk.CTkLabel(
                parent, text=hint,
                font=ctk.CTkFont(size=10),
                text_color=("#94A3B8", "#64748B"), anchor="w",
            ).grid(row=row + 1, column=0, sticky="w", padx=(0, 16), pady=(0, 2))
        return row + (2 if hint else 1)

    # ── 1. Calculation Settings ───────────────────────────────────────
    def _build_calculation_card(self) -> None:
        inner = self._card(1, "⚙️  Calculation Settings", BLUE)
        r = 0

        # Default epsilon
        r = self._row(inner, r, "Default Epsilon (Tolerance)", "Stopping criterion for error")
        self._vars["default_epsilon"] = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self._vars["default_epsilon"],
                     width=140).grid(row=r - 2, column=1, sticky="w", pady=(6, 0))

        # Max iterations
        r = self._row(inner, r, "Default Max Iterations")
        self._vars["default_max_iter"] = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self._vars["default_max_iter"],
                     width=140).grid(row=r - 1, column=1, sticky="w")

        # Decimal places
        r = self._row(inner, r, "Default Decimal Places")
        self._vars["default_decimal_places"] = ctk.StringVar()
        ctk.CTkComboBox(inner, values=["2", "3", "4", "5", "6", "8", "10"],
                        variable=self._vars["default_decimal_places"],
                        width=140).grid(row=r - 1, column=1, sticky="w")

        # Default stop condition
        r = self._row(inner, r, "Default Stop Condition")
        self._vars["default_stop_condition"] = ctk.StringVar()
        ctk.CTkComboBox(inner,
                        values=["epsilon", "max_iterations"],
                        variable=self._vars["default_stop_condition"],
                        width=200).grid(row=r - 1, column=1, sticky="w")

        # Default nonlinear method
        r = self._row(inner, r, "Default Non-Linear Method")
        self._vars["default_nonlinear_method"] = ctk.StringVar()
        ctk.CTkComboBox(inner,
                        values=["Bisection", "False Position", "Fixed Point",
                                "Newton-Raphson", "Secant"],
                        variable=self._vars["default_nonlinear_method"],
                        width=220).grid(row=r - 1, column=1, sticky="w")

        # Default linear method
        r = self._row(inner, r, "Default Linear Method")
        self._vars["default_linear_method"] = ctk.StringVar()
        ctk.CTkComboBox(inner,
                        values=["Gauss Elimination", "LU Decomposition",
                                "Gauss-Jordan", "Cramer's Rule"],
                        variable=self._vars["default_linear_method"],
                        width=220).grid(row=r - 1, column=1, sticky="w")

        # Enable rounding
        self._vars["enable_rounding"] = ctk.BooleanVar()
        ctk.CTkCheckBox(inner, text="Enable result rounding by default",
                        variable=self._vars["enable_rounding"]
                        ).grid(row=r, column=0, columnspan=2, sticky="w", pady=4)

    # ── 2. UI Settings ────────────────────────────────────────────────
    def _build_ui_card(self) -> None:
        inner = self._card(2, "🎨  User Interface Settings", PURPLE)
        r = 0

        # Theme
        r = self._row(inner, r, "Application Theme")
        self._vars["appearance_mode"] = ctk.StringVar()
        ctk.CTkSegmentedButton(
            inner,
            values=["light", "dark", "system"],
            variable=self._vars["appearance_mode"],
            command=self._on_theme_change,
            width=260,
        ).grid(row=r - 1, column=1, sticky="w")

        # Font size
        r = self._row(inner, r, "Font Size", "Affects entry and label text throughout")
        self._vars["font_size"] = ctk.StringVar()
        ctk.CTkComboBox(inner, values=["10", "11", "12", "13", "14", "15", "16"],
                        variable=self._vars["font_size"],
                        width=140).grid(row=r - 2, column=1, sticky="w", pady=(6, 0))

        # Toggles
        for key, label in (
            ("auto_save_results",    "Auto-save results to history"),
            ("show_graph_automatically", "Show graph automatically after solving"),
            ("show_step_by_step",   "Show step-by-step solution"),
        ):
            self._vars[key] = ctk.BooleanVar()
            ctk.CTkCheckBox(inner, text=label,
                            variable=self._vars[key]
                            ).grid(row=r, column=0, columnspan=2, sticky="w", pady=3)
            r += 1

    # ── 3. Export Settings ────────────────────────────────────────────
    def _build_export_card(self) -> None:
        inner = self._card(3, "📄  Export Settings", "#059669")
        r = 0

        # Export folder
        r = self._row(inner, r, "Default PDF Export Folder")
        folder_frame = ctk.CTkFrame(inner, fg_color="transparent")
        folder_frame.grid(row=r - 1, column=1, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)
        self._vars["pdf_export_folder"] = ctk.StringVar()
        ctk.CTkEntry(folder_frame, textvariable=self._vars["pdf_export_folder"]
                     ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(folder_frame, text="Browse", width=70,
                      command=self._browse_folder
                      ).grid(row=0, column=1)

        # Custom PDF title
        r = self._row(inner, r, "Custom PDF Report Title")
        self._vars["custom_pdf_title"] = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self._vars["custom_pdf_title"],
                     width=300).grid(row=r - 1, column=1, sticky="w")

        # Paper size
        r = self._row(inner, r, "PDF Paper Size")
        self._vars["pdf_paper_size"] = ctk.StringVar()
        ctk.CTkComboBox(inner, values=["A4", "Letter"],
                        variable=self._vars["pdf_paper_size"],
                        width=140).grid(row=r - 1, column=1, sticky="w")

        # Toggles
        for key, label in (
            ("include_graph_in_pdf",    "Include graph/figure in PDF"),
            ("include_table_in_pdf",    "Include iteration table in PDF"),
            ("include_datetime_in_pdf", "Include date and time in PDF header"),
        ):
            self._vars[key] = ctk.BooleanVar()
            ctk.CTkCheckBox(inner, text=label,
                            variable=self._vars[key]
                            ).grid(row=r, column=0, columnspan=2, sticky="w", pady=3)
            r += 1

    # ── 4. History Settings ───────────────────────────────────────────
    def _build_history_card(self) -> None:
        inner = self._card(4, "🕓  History Settings", "#F59E0B")
        r = 0

        self._vars["enable_history"] = ctk.BooleanVar()
        ctk.CTkCheckBox(inner, text="Enable history saving",
                        variable=self._vars["enable_history"]
                        ).grid(row=r, column=0, columnspan=2, sticky="w", pady=4)
        r += 1

        r = self._row(inner, r, "Maximum Saved Records",
                      "Oldest records are removed when limit is reached")
        self._vars["max_history_entries"] = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self._vars["max_history_entries"],
                     width=120).grid(row=r - 2, column=1, sticky="w", pady=(6, 0))

        ctk.CTkButton(
            inner, text="Clear All History",
            fg_color="#EF4444", hover_color="#DC2626",
            command=self._clear_history, width=180,
        ).grid(row=r, column=0, columnspan=2, sticky="w", pady=(8, 4))

    # ── 5. Advanced Settings ──────────────────────────────────────────
    def _build_advanced_card(self) -> None:
        inner = self._card(5, "🔬  Advanced Settings", "#6366F1")
        r = 0

        for key, label in (
            ("enable_advanced_validation",  "Enable advanced input validation"),
            ("show_convergence_warnings",   "Show warnings for non-convergence"),
        ):
            self._vars[key] = ctk.BooleanVar()
            ctk.CTkCheckBox(inner, text=label,
                            variable=self._vars[key]
                            ).grid(row=r, column=0, columnspan=2, sticky="w", pady=3)
            r += 1

    # ── Save / Reset row ──────────────────────────────────────────────
    def _build_save_row(self) -> None:
        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.grid(row=6, column=0, sticky="ew", padx=36, pady=(12, 32))
        row_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            row_frame, text="💾  Save Changes",
            fg_color=BLUE, hover_color="#1D4ED8",
            height=40, font=ctk.CTkFont(size=13, weight="bold"),
            command=self._save,
            width=180,
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            row_frame, text="↺  Reset to Defaults",
            fg_color="#64748B", hover_color="#475569",
            height=40, font=ctk.CTkFont(size=13),
            command=self._reset,
            width=180,
        ).grid(row=0, column=1)

        self._status_label = ctk.CTkLabel(
            row_frame, text="",
            font=ctk.CTkFont(size=12),
            text_color="#059669",
        )
        self._status_label.grid(row=0, column=2, padx=16, sticky="w")

    # ── Load / Save / Reset ───────────────────────────────────────────
    def _load_values(self) -> None:
        s = self.sm.all()
        for key, var in self._vars.items():
            val = s.get(key)
            if val is None:
                continue
            try:
                if isinstance(var, ctk.BooleanVar):
                    var.set(bool(val))
                else:
                    var.set(str(val))
            except Exception:
                pass

    def _save(self) -> None:
        new_settings = {}
        for key, var in self._vars.items():
            try:
                raw = var.get()
                # Coerce numeric fields
                if key in ("default_epsilon",):
                    new_settings[key] = float(raw)
                elif key in ("default_max_iter", "default_decimal_places",
                             "max_history_entries", "font_size"):
                    new_settings[key] = int(float(raw))
                elif isinstance(var, ctk.BooleanVar):
                    new_settings[key] = bool(raw)
                else:
                    new_settings[key] = raw
            except Exception:
                new_settings[key] = var.get()

        self.sm.save(new_settings)
        self._status_label.configure(text="✓  Settings saved successfully!")
        self.after(3000, lambda: self._status_label.configure(text=""))

    def _reset(self) -> None:
        self.sm.reset()
        self._load_values()
        self._status_label.configure(text="↺  Reset to defaults.")
        self.after(2500, lambda: self._status_label.configure(text=""))

    def _on_theme_change(self, value: str) -> None:
        self.controller.apply_theme(value)

    def _browse_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select PDF Export Folder")
        if folder:
            self._vars["pdf_export_folder"].set(folder)

    def _clear_history(self) -> None:
        dialog = ctk.CTkInputDialog(
            text="Type CONFIRM to clear all history records:",
            title="Clear History",
        )
        answer = dialog.get_input()
        if answer and answer.strip().upper() == "CONFIRM":
            history_page = self.controller.pages.get("history")
            if history_page and hasattr(history_page, "_history_manager"):
                history_page._history_manager.clear_all()
                history_page.refresh()
            self._status_label.configure(text="✓  History cleared.")
            self.after(2500, lambda: self._status_label.configure(text=""))
