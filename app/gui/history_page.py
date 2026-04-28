import json
from datetime import datetime
from tkinter import filedialog

import customtkinter as ctk

from app.services.history_manager import HistoryManager
from app.services import pdf_exporter


BLUE   = "#2563EB"
PURPLE = "#7C3AED"
GREEN  = "#059669"
BG_CARD = ("white", "#1E293B")
BORDER  = ("#E2E8F0", "#334155")
TYPE_COLORS = {"nonlinear": BLUE, "linear": PURPLE}


class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, controller, history_manager: HistoryManager) -> None:
        super().__init__(parent, corner_radius=0, fg_color=("white", "#0F172A"))
        self._history_manager = history_manager
        self.controller = controller
        self._selected_id: str | None = None
        self._record_buttons: dict[str, ctk.CTkButton] = {}

        self.grid_columnconfigure(0, weight=0, minsize=320)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()
        self.refresh()

    # ── Left panel ────────────────────────────────────────────────────
    def _build_left_panel(self) -> None:
        left = ctk.CTkFrame(
            self, fg_color=("white", "#1E293B"),
            corner_radius=0, border_width=1, border_color=BORDER,
        )
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(left, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            hdr, text="Solution History",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"), anchor="w",
        ).grid(row=0, column=0, sticky="w")

        # Search
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter_list())
        ctk.CTkEntry(
            left,
            textvariable=self._search_var,
            placeholder_text="🔍  Search by method or date…",
            height=32,
        ).grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 6))

        # Scrollable record list
        self._list_frame = ctk.CTkScrollableFrame(
            left, fg_color="transparent", corner_radius=0,
        )
        self._list_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self._list_frame.grid_columnconfigure(0, weight=1)

        # Bottom buttons
        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=14, pady=10)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text="Delete Selected",
            fg_color="#EF4444", hover_color="#DC2626",
            height=34, font=ctk.CTkFont(size=12),
            command=self._delete_selected,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkButton(
            btn_frame, text="Clear All",
            fg_color="#64748B", hover_color="#475569",
            height=34, font=ctk.CTkFont(size=12),
            command=self._clear_all,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    # ── Right panel ───────────────────────────────────────────────────
    def _build_right_panel(self) -> None:
        right = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "#0F172A"))
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Action bar
        action_bar = ctk.CTkFrame(right, fg_color=("white", "#1E293B"),
                                  corner_radius=0, border_width=0)
        action_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        action_bar.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            action_bar, text="Record Details",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
        ).grid(row=0, column=0, padx=20, pady=12, sticky="w")

        ctk.CTkButton(
            action_bar, text="📄  Export PDF",
            fg_color=GREEN, hover_color="#047857",
            height=32, font=ctk.CTkFont(size=12),
            command=self._export_pdf,
            width=130,
        ).grid(row=0, column=1, padx=8, pady=10)

        # Detail textbox
        detail_frame = ctk.CTkFrame(right, fg_color="transparent")
        detail_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=12)
        detail_frame.grid_rowconfigure(0, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)

        self._detail_box = ctk.CTkTextbox(
            detail_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        self._detail_box.grid(row=0, column=0, sticky="nsew")

    # ── Public API ────────────────────────────────────────────────────
    def refresh(self) -> None:
        self._all_records = self._history_manager.load_records()
        self._filter_list()

    # ── Internal helpers ──────────────────────────────────────────────
    def _filter_list(self) -> None:
        query = self._search_var.get().lower().strip()
        records = [
            r for r in self._all_records
            if not query
            or query in r.get("method", "").lower()
            or query in r.get("datetime", "").lower()
            or query in r.get("type", "").lower()
        ]
        self._populate_list(records)

    def _populate_list(self, records: list[dict]) -> None:
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._record_buttons.clear()
        self._list_frame.grid_columnconfigure(0, weight=1)

        if not records:
            ctk.CTkLabel(
                self._list_frame,
                text="No records found.",
                font=ctk.CTkFont(size=12),
                text_color=("#94A3B8", "#64748B"),
            ).grid(row=0, column=0, pady=30)
            return

        for idx, record in enumerate(records):
            rid = record.get("id", "")
            dt_str = record.get("datetime", "")
            try:
                dt_fmt = datetime.fromisoformat(dt_str).strftime("%b %d, %Y  %H:%M")
            except Exception:
                dt_fmt = dt_str

            rtype = record.get("type", "nonlinear")
            method = record.get("method", "Unknown")
            color = TYPE_COLORS.get(rtype, BLUE)

            # Use CTkFrame as the card — CTkButton cannot host child widgets
            card = ctk.CTkFrame(
                self._list_frame,
                fg_color=("white", "#1E293B"),
                corner_radius=8,
                border_width=1,
                border_color=BORDER,
                cursor="hand2",
            )
            card.grid(row=idx, column=0, sticky="ew", padx=8, pady=3)
            card.grid_columnconfigure(1, weight=1)

            def _click(e, r=record):
                self._on_record_selected(r)

            card.bind("<Button-1>", _click)

            # Badge
            badge = ctk.CTkLabel(
                card,
                text=rtype.upper(),
                font=ctk.CTkFont(size=8, weight="bold"),
                fg_color=color, text_color="white",
                corner_radius=4, padx=5, pady=1,
            )
            badge.grid(row=0, column=0, sticky="w", padx=(10, 4), pady=(8, 2))
            badge.bind("<Button-1>", _click)

            # Method name
            lbl_method = ctk.CTkLabel(
                card,
                text=method,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#1E293B", "#F1F5F9"), anchor="w",
            )
            lbl_method.grid(row=0, column=1, sticky="w", padx=4, pady=(8, 2))
            lbl_method.bind("<Button-1>", _click)

            # Date
            lbl_date = ctk.CTkLabel(
                card,
                text=dt_fmt,
                font=ctk.CTkFont(size=10),
                text_color=("#94A3B8", "#64748B"), anchor="w",
            )
            lbl_date.grid(row=1, column=0, columnspan=2, sticky="w",
                          padx=10, pady=(0, 8))
            lbl_date.bind("<Button-1>", _click)

            self._record_buttons[rid] = card

        # Re-highlight selected
        if self._selected_id and self._selected_id in self._record_buttons:
            self._highlight(self._selected_id)

    def _on_record_selected(self, record: dict) -> None:
        self._selected_id = record.get("id")
        self._highlight(self._selected_id)
        self._display_record(record)

    def _highlight(self, rid: str) -> None:
        for key, btn in self._record_buttons.items():
            if key == rid:
                btn.configure(fg_color=("#DBEAFE", "#1E3A5F"))
            else:
                btn.configure(fg_color=("white", "#1E293B"))

    def _display_record(self, record: dict) -> None:
        rtype = record.get("type", "")
        method = record.get("method", "")
        dt_str = record.get("datetime", "")
        inputs = record.get("inputs", {})
        result = record.get("result", {})
        converged = result.get("converged", False)
        iterations = result.get("iterations_count", "N/A")

        lines = [
            "=" * 55,
            f"  Record ID  : {record.get('id', '')}",
            f"  Date/Time  : {dt_str}",
            f"  Type       : {rtype.upper()}",
            f"  Method     : {method}",
            "=" * 55,
            "",
            "  INPUT PARAMETERS",
            "  " + "-" * 40,
        ]
        for k, v in inputs.items():
            lines.append(f"  {str(k):<22}: {v}")

        lines += ["", "  RESULT", "  " + "-" * 40]

        if rtype == "nonlinear":
            root = result.get("root_or_solution", "N/A")
            err  = result.get("final_error", "N/A")
            lines.append(f"  Root               : {root}")
            lines.append(f"  Final Error (%)    : {err}")
        else:
            sol = result.get("root_or_solution", [])
            if isinstance(sol, list):
                for i, v in enumerate(sol):
                    lines.append(f"  x{i+1}                 : {v}")
            else:
                lines.append(f"  Solution           : {sol}")

        lines.append(f"  Iterations         : {iterations}")
        lines.append(f"  Converged          : {'Yes ✓' if converged else 'No ✗'}")
        lines.append("")
        lines.append("=" * 55)

        self._detail_box.configure(state="normal")
        self._detail_box.delete("1.0", "end")
        self._detail_box.insert("1.0", "\n".join(lines))
        self._detail_box.configure(state="disabled")

    def _delete_selected(self) -> None:
        if not self._selected_id:
            return
        self._history_manager.delete_record(self._selected_id)
        self._selected_id = None
        self._detail_box.configure(state="normal")
        self._detail_box.delete("1.0", "end")
        self._detail_box.configure(state="disabled")
        self.refresh()

    def _clear_all(self) -> None:
        dialog = ctk.CTkInputDialog(
            text="Type CONFIRM to delete all history records:",
            title="Clear All History",
        )
        answer = dialog.get_input()
        if answer and answer.strip().upper() == "CONFIRM":
            self._history_manager.clear_all()
            self._selected_id = None
            self._detail_box.configure(state="normal")
            self._detail_box.delete("1.0", "end")
            self._detail_box.configure(state="disabled")
            self.refresh()

    def _export_pdf(self) -> None:
        if not self._selected_id:
            return
        record = self._history_manager.get_record(self._selected_id)
        if not record:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"history_{self._selected_id}.pdf",
            title="Save PDF",
        )
        if not filepath:
            return

        try:
            rtype = record.get("type", "nonlinear")
            inputs = record.get("inputs", {})
            result_data = {
                "method": record.get("method", ""),
                "root": record.get("result", {}).get("root_or_solution", ""),
                "final_error": record.get("result", {}).get("final_error", ""),
                "converged": record.get("result", {}).get("converged", False),
                "iterations_count": record.get("result", {}).get("iterations_count", 0),
                "iterations": [],
                "solution": record.get("result", {}).get("root_or_solution", []),
                "steps": [],
                "extra": {},
            }
            if rtype == "nonlinear":
                pdf_exporter.export_nonlinear_pdf(filepath, result_data, inputs)
            else:
                A = inputs.get("A", [])
                b = inputs.get("b", [])
                pdf_exporter.export_linear_pdf(filepath, result_data, {"A": A, "b": b})
        except ImportError as e:
            self._show_pdf_error(str(e))
        except Exception as e:
            self._show_pdf_error(str(e))

    def _show_pdf_error(self, msg: str) -> None:
        win = ctk.CTkToplevel(self)
        win.title("PDF Export Error")
        win.geometry("440x160")
        win.grab_set()
        ctk.CTkLabel(win, text=msg, wraplength=400,
                     font=ctk.CTkFont(size=12)).pack(expand=True, padx=20)
        ctk.CTkButton(win, text="OK", command=win.destroy, width=80).pack(pady=10)
