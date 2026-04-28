"""Linear system solver page.
Left panel: matrix size, method, examples, dynamic A|b grid, buttons.
Right panel: solution vector, step-by-step text, extra matrices, export.
"""
from tkinter import filedialog
import customtkinter as ctk

from app.services.settings_manager import SettingsManager
from app.services.history_manager import HistoryManager
from app.methods import linear as lm
from app.utils import validators
from app.services import pdf_exporter


BLUE   = "#2563EB"
PURPLE = "#7C3AED"
GREEN  = "#059669"
RED    = "#EF4444"
BG_CARD = ("white", "#1E293B")
BORDER  = ("#E2E8F0", "#334155")

METHODS = [
    "Gauss Elimination",
    "LU Decomposition",
    "Gauss-Jordan",
    "Cramer's Rule",
]

EXAMPLES = {
    "Example 1  (3×3)": {
        "size": 3,
        "A": [[2, 1, 1], [3, 4, 0], [2, 3, 1]],
        "b": [8, 11, 13],
    },
    "Example 2  (3×3)": {
        "size": 3,
        "A": [[3, 2, -1], [2, -2, 4], [-1, 0.5, -1]],
        "b": [1, -2, 0],
    },
    "Example 3  (2×2)": {
        "size": 2,
        "A": [[4, 1], [2, 3]],
        "b": [9, 8],
    },
    "Example 4  (4×4)": {
        "size": 4,
        "A": [[2, 1, -1, 1],
              [3, 2,  0, -2],
              [-1, 1, 3, 1],
              [1, -1, 2, 4]],
        "b": [3, 1, 7, 5],
    },
}

SIZES = [2, 3, 4]


class LinearPage(ctk.CTkFrame):
    def __init__(self, parent, controller,
                 settings_manager: SettingsManager,
                 history_manager: HistoryManager) -> None:
        super().__init__(parent, corner_radius=0, fg_color=("white", "#0F172A"))
        self.controller = controller
        self.sm = settings_manager
        self.hm = history_manager

        self._matrix_size: int = 3
        self._matrix_entries: list[list[ctk.CTkEntry]] = []
        self._vector_entries: list[ctk.CTkEntry] = []
        self._last_result: dict | None = None
        self._last_inputs: dict | None = None

        self.grid_columnconfigure(0, weight=0, minsize=420)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

    # ════════════════════════════════════════════════════════════════
    # LEFT PANEL
    # ════════════════════════════════════════════════════════════════
    def _build_left_panel(self) -> None:
        left = ctk.CTkScrollableFrame(
            self,
            fg_color=("white", "#1E293B"),
            corner_radius=0,
            border_width=1,
            border_color=BORDER,
        )
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        self._left = left

        # ── Title ──────────────────────────────────────────────────
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 4))
        ctk.CTkLabel(
            title_frame,
            text="Linear Systems Solver",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"), anchor="w",
        ).pack(anchor="w")
        ctk.CTkFrame(title_frame, height=2, fg_color=PURPLE, corner_radius=2
                     ).pack(fill="x", pady=(6, 0))

        # ── Matrix Size ────────────────────────────────────────────
        ctk.CTkLabel(left, text="Matrix Size",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=("#374151", "#CBD5E1"), anchor="w",
                     ).grid(row=1, column=0, sticky="w", padx=16, pady=(12, 2))

        self._size_combo = ctk.CTkSegmentedButton(
            left,
            values=["2x2", "3x3", "4x4"],
            command=self._on_size_changed,
        )
        self._size_combo.set("3x3")
        self._size_combo.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

        # ── Method ─────────────────────────────────────────────────
        ctk.CTkLabel(left, text="Method",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=("#374151", "#CBD5E1"), anchor="w",
                     ).grid(row=3, column=0, sticky="w", padx=16, pady=(2, 2))

        self._method_combo = ctk.CTkComboBox(
            left, values=METHODS,
        )
        default_method = self.sm.get("default_linear_method", "Gauss Elimination")
        self._method_combo.set(default_method)
        self._method_combo.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 4))

        # ── Examples ───────────────────────────────────────────────
        ctk.CTkLabel(left, text="Load Example",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=("#374151", "#CBD5E1"), anchor="w",
                     ).grid(row=5, column=0, sticky="w", padx=16, pady=(10, 2))
        self._example_combo = ctk.CTkComboBox(
            left,
            values=["-- Select example --"] + list(EXAMPLES.keys()),
            command=self._on_example_selected,
        )
        self._example_combo.set("-- Select example --")
        self._example_combo.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 8))

        # ── Matrix grid container ──────────────────────────────────
        ctk.CTkLabel(left, text="Matrix  A  and Vector  b",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=("#374151", "#CBD5E1"), anchor="w",
                     ).grid(row=7, column=0, sticky="w", padx=16, pady=(4, 4))

        self._matrix_container = None   # created fresh inside _build_matrix_grid
        self._build_matrix_grid(self._matrix_size)

        # ── Decimal places ─────────────────────────────────────────
        dp_frame = ctk.CTkFrame(left, fg_color="transparent")
        dp_frame.grid(row=9, column=0, sticky="ew", padx=16, pady=(4, 4))
        ctk.CTkLabel(dp_frame, text="Decimal places:",
                     font=ctk.CTkFont(size=11),
                     text_color=("#374151", "#CBD5E1"),
                     ).pack(side="left", padx=(0, 8))
        self._dp_combo = ctk.CTkComboBox(
            dp_frame, values=["2", "3", "4", "5", "6", "8", "10"],
            width=100,
        )
        self._dp_combo.set(str(self.sm.get("default_decimal_places", 6)))
        self._dp_combo.pack(side="left")

        # ── Buttons ────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.grid(row=10, column=0, sticky="ew", padx=16, pady=(10, 20))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text="▶  Solve",
            fg_color=PURPLE, hover_color="#6D28D9",
            height=40, font=ctk.CTkFont(size=13, weight="bold"),
            command=self._solve,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            btn_frame, text="✕  Clear",
            fg_color="#64748B", hover_color="#475569",
            height=40, font=ctk.CTkFont(size=13),
            command=self._clear,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _build_matrix_grid(self, n: int) -> None:
        """Recreate the A|b entry grid for an n×n system using stretchy columns."""
        # Destroy old container entirely so no stale column configs remain
        if self._matrix_container is not None:
            self._matrix_container.destroy()

        self._matrix_container = ctk.CTkFrame(
            self._left,
            fg_color=("white", "#1E293B"),
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        self._matrix_container.grid(row=8, column=0, sticky="ew", padx=16, pady=(0, 8))

        self._matrix_entries = []
        self._vector_entries = []

        # Column 0: row labels (fixed narrow)
        self._matrix_container.grid_columnconfigure(0, weight=0, minsize=36)
        # Columns 1..n: A entries — stretch equally
        for j in range(1, n + 1):
            self._matrix_container.grid_columnconfigure(j, weight=1, minsize=44)
        # Column n+1: "=" separator (fixed)
        self._matrix_container.grid_columnconfigure(n + 1, weight=0, minsize=18)
        # Column n+2: b entry — stretch like A entries
        self._matrix_container.grid_columnconfigure(n + 2, weight=1, minsize=44)

        # ── Header row ─────────────────────────────────────────────
        for j in range(n):
            ctk.CTkLabel(
                self._matrix_container,
                text=f"x{j+1}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=PURPLE,
                anchor="center",
            ).grid(row=0, column=j + 1, padx=3, pady=(8, 2), sticky="ew")

        ctk.CTkLabel(
            self._matrix_container,
            text="=",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#374151", "#CBD5E1"),
        ).grid(row=0, column=n + 1, pady=(8, 2))

        ctk.CTkLabel(
            self._matrix_container,
            text="b",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=GREEN,
            anchor="center",
        ).grid(row=0, column=n + 2, padx=3, pady=(8, 2), sticky="ew")

        # ── Data rows ──────────────────────────────────────────────
        for i in range(n):
            ctk.CTkLabel(
                self._matrix_container,
                text=f"Eq {i+1}",
                font=ctk.CTkFont(size=10),
                text_color=("#94A3B8", "#64748B"),
                anchor="e",
            ).grid(row=i + 1, column=0, padx=(8, 4), pady=4, sticky="e")

            row_entries = []
            for j in range(n):
                e = ctk.CTkEntry(
                    self._matrix_container,
                    height=32,
                    justify="center",
                    font=ctk.CTkFont(size=11),
                )
                e.grid(row=i + 1, column=j + 1, padx=3, pady=4, sticky="ew")
                row_entries.append(e)
            self._matrix_entries.append(row_entries)

            ctk.CTkLabel(
                self._matrix_container,
                text="=",
                font=ctk.CTkFont(size=12),
                text_color=("#374151", "#CBD5E1"),
            ).grid(row=i + 1, column=n + 1)

            b_e = ctk.CTkEntry(
                self._matrix_container,
                height=32,
                justify="center",
                font=ctk.CTkFont(size=11),
                border_color=GREEN,
            )
            b_e.grid(row=i + 1, column=n + 2, padx=3, pady=4, sticky="ew")
            self._vector_entries.append(b_e)

        # Bottom spacing
        ctk.CTkFrame(self._matrix_container, height=8, fg_color="transparent"
                     ).grid(row=n + 1, column=0, columnspan=n + 3)

    # ════════════════════════════════════════════════════════════════
    # RIGHT PANEL
    # ════════════════════════════════════════════════════════════════
    def _build_right_panel(self) -> None:
        right = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "#0F172A"))
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)
        self._right = right

        # Action bar
        bar = ctk.CTkFrame(right, fg_color=("white", "#1E293B"),
                           corner_radius=0, border_width=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            bar, text="Results",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self._export_btn = ctk.CTkButton(
            bar, text="📄  Export PDF",
            fg_color=GREEN, hover_color="#047857",
            height=32, font=ctk.CTkFont(size=12),
            command=self._export_pdf,
            state="disabled",
            width=130,
        )
        self._export_btn.grid(row=0, column=1, padx=8, pady=8)

        self._status_label = ctk.CTkLabel(
            bar, text="Enter a system and click Solve.",
            font=ctk.CTkFont(size=11),
            text_color=("#64748B", "#94A3B8"),
        )
        self._status_label.grid(row=0, column=2, padx=12, sticky="w")

        # Scrollable results
        self._results_scroll = ctk.CTkScrollableFrame(
            right, corner_radius=0, fg_color="transparent",
        )
        self._results_scroll.grid(row=1, column=0, sticky="nsew")
        self._results_scroll.grid_columnconfigure(0, weight=1)

        # Pre-build result cards (hidden initially)
        self._solution_card = ctk.CTkFrame(
            self._results_scroll, corner_radius=12,
            fg_color=BG_CARD, border_width=1, border_color=BORDER,
        )
        self._steps_card = ctk.CTkFrame(
            self._results_scroll, corner_radius=12,
            fg_color=BG_CARD, border_width=1, border_color=BORDER,
        )
        self._extra_card = ctk.CTkFrame(
            self._results_scroll, corner_radius=12,
            fg_color=BG_CARD, border_width=1, border_color=BORDER,
        )

        self._placeholder = ctk.CTkLabel(
            self._results_scroll,
            text="No results yet.\nFill the matrix and click  ▶ Solve",
            font=ctk.CTkFont(size=13),
            text_color=("#94A3B8", "#64748B"),
        )
        self._placeholder.grid(row=10, column=0, pady=60)

    # ════════════════════════════════════════════════════════════════
    # EVENTS
    # ════════════════════════════════════════════════════════════════
    def _on_size_changed(self, value: str) -> None:
        size_map = {"2x2": 2, "3x3": 3, "4x4": 4}
        n = size_map.get(value, 3)
        self._matrix_size = n
        self._build_matrix_grid(n)

    def _on_example_selected(self, value: str) -> None:
        if value.startswith("--"):
            return
        ex = EXAMPLES.get(value)
        if not ex:
            return
        n = ex["size"]
        # Update size selector
        sz_label = f"{n}x{n}"
        self._size_combo.set(sz_label)
        self._matrix_size = n
        self._build_matrix_grid(n)
        self._populate_example(ex["A"], ex["b"])

    def _populate_example(self, A: list, b: list) -> None:
        for i, row in enumerate(A):
            for j, val in enumerate(row):
                e = self._matrix_entries[i][j]
                e.delete(0, "end")
                e.insert(0, str(val))
        for i, val in enumerate(b):
            e = self._vector_entries[i]
            e.delete(0, "end")
            e.insert(0, str(val))

    # ════════════════════════════════════════════════════════════════
    # COLLECT INPUTS
    # ════════════════════════════════════════════════════════════════
    def _collect_matrix_inputs(self) -> tuple | None:
        A_strs = [[e.get() for e in row] for row in self._matrix_entries]
        b_strs = [e.get() for e in self._vector_entries]

        ok, msg = validators.validate_matrix(A_strs, b_strs)
        if not ok:
            self._show_error(msg)
            return None

        A = [[float(v) for v in row] for row in A_strs]
        b = [float(v) for v in b_strs]
        return A, b

    # ════════════════════════════════════════════════════════════════
    # SOLVE
    # ════════════════════════════════════════════════════════════════
    def _solve(self) -> None:
        data = self._collect_matrix_inputs()
        if data is None:
            return
        A, b = data
        method = self._method_combo.get()
        dp = int(self._dp_combo.get())

        try:
            if method == "Gauss Elimination":
                result = lm.solve_gauss_elimination(A, b, dp)
            elif method == "LU Decomposition":
                result = lm.solve_lu_decomposition(A, b, dp)
            elif method == "Gauss-Jordan":
                result = lm.solve_gauss_jordan(A, b, dp)
            elif method == "Cramer's Rule":
                result = lm.solve_cramers_rule(A, b, dp)
            else:
                self._show_error(f"Unknown method: {method}")
                return
        except Exception as exc:
            self._show_error(str(exc))
            return

        self._last_result = result
        self._last_inputs = {"A": A, "b": b, "method": method, "size": len(b), "decimal_places": dp}
        self._display_results(result)

        if self.sm.get("auto_save_results", True):
            self._save_history(result, A, b)

    def _display_results(self, result: dict) -> None:
        self._placeholder.grid_remove()
        sol = result.get("solution", [])
        sol_str = "  ".join(f"x{i+1}={v}" for i, v in enumerate(sol))
        self._show_success(f"✓  Solved  |  {sol_str}")
        self._populate_solution_card(result)
        self._populate_steps_card(result)
        self._populate_extra_card(result)
        self._export_btn.configure(state="normal")

    # ── Solution card ─────────────────────────────────────────────
    def _populate_solution_card(self, result: dict) -> None:
        for w in self._solution_card.winfo_children():
            w.destroy()

        ctk.CTkFrame(self._solution_card, height=3, fg_color=GREEN, corner_radius=0
                     ).grid(row=0, column=0, columnspan=8, sticky="ew")
        ctk.CTkLabel(
            self._solution_card, text="Solution Vector",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
        ).grid(row=1, column=0, columnspan=8, sticky="w", padx=16, pady=(10, 8))

        solution = result.get("solution", [])
        sol_row = ctk.CTkFrame(self._solution_card, fg_color="transparent")
        sol_row.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))

        for i, val in enumerate(solution):
            f = ctk.CTkFrame(sol_row, fg_color=("white", "#0F172A"),
                             corner_radius=8, border_width=1, border_color=BORDER)
            f.pack(side="left", padx=6, pady=2)
            ctk.CTkLabel(
                f, text=f"x{i+1}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=("#64748B", "#94A3B8"),
            ).pack(padx=12, pady=(6, 0))
            ctk.CTkLabel(
                f, text=str(val),
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=GREEN,
            ).pack(padx=12, pady=(0, 8))

        self._solution_card.grid_columnconfigure(0, weight=1)
        self._solution_card.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))

    # ── Steps card ────────────────────────────────────────────────
    def _populate_steps_card(self, result: dict) -> None:
        for w in self._steps_card.winfo_children():
            w.destroy()

        show = self.sm.get("show_step_by_step", True)
        if not show:
            return

        ctk.CTkFrame(self._steps_card, height=3, fg_color=BLUE, corner_radius=0
                     ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            self._steps_card,
            text=f"Step-by-Step Solution  —  {result.get('method', '')}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(10, 6))

        steps = result.get("steps", [])
        steps_text = "\n".join(steps)

        txt = ctk.CTkTextbox(
            self._steps_card,
            font=ctk.CTkFont(family="Consolas", size=10),
            height=260,
            corner_radius=6,
            border_width=1,
            border_color=BORDER,
        )
        txt.insert("1.0", steps_text)
        txt.configure(state="disabled")
        txt.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        self._steps_card.grid_columnconfigure(0, weight=1)
        self._steps_card.grid(row=1, column=0, sticky="ew", padx=16, pady=6)

    # ── Extra card (LU, Cramer) ────────────────────────────────────
    def _populate_extra_card(self, result: dict) -> None:
        for w in self._extra_card.winfo_children():
            w.destroy()

        extra = result.get("extra", {})
        if not extra:
            self._extra_card.grid_remove()
            return

        ctk.CTkFrame(self._extra_card, height=3, fg_color=PURPLE, corner_radius=0
                     ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            self._extra_card, text="Additional Details",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(10, 6))
        self._extra_card.grid_columnconfigure(0, weight=1)

        inner_row = 2

        if "L" in extra and "U" in extra:
            cols = ctk.CTkFrame(self._extra_card, fg_color="transparent")
            cols.grid(row=inner_row, column=0, sticky="ew", padx=16, pady=(0, 12))
            cols.grid_columnconfigure((0, 1), weight=1)

            def matrix_display(parent, col, label, M):
                f = ctk.CTkFrame(parent, fg_color=("white", "#0F172A"),
                                 corner_radius=8, border_width=1, border_color=BORDER)
                f.grid(row=0, column=col, sticky="nsew", padx=4)
                ctk.CTkLabel(f, text=label,
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=PURPLE).pack(padx=10, pady=(8, 4))
                mat_str = "\n".join(
                    "  " + "  ".join(f"{v:>9.4f}" for v in row) for row in M
                )
                ctk.CTkLabel(
                    f, text=mat_str,
                    font=ctk.CTkFont(family="Consolas", size=10),
                    text_color=("#374151", "#CBD5E1"),
                    justify="left",
                ).pack(padx=10, pady=(0, 10))

            matrix_display(cols, 0, "L  (Lower Triangular)", extra["L"])
            matrix_display(cols, 1, "U  (Upper Triangular)", extra["U"])

        if "det_A" in extra:
            det_frame = ctk.CTkFrame(self._extra_card, fg_color="transparent")
            det_frame.grid(row=inner_row, column=0, sticky="ew", padx=16, pady=(0, 12))
            ctk.CTkLabel(
                det_frame,
                text=f"det(A) = {extra['det_A']}",
                font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                text_color=PURPLE,
            ).pack(anchor="w")
            for i, d in enumerate(extra.get("det_Ai", [])):
                ctk.CTkLabel(
                    det_frame,
                    text=f"det(A{i+1}) = {d}",
                    font=ctk.CTkFont(family="Consolas", size=11),
                    text_color=("#374151", "#CBD5E1"),
                ).pack(anchor="w")

        self._extra_card.grid(row=2, column=0, sticky="ew", padx=16, pady=6)

    # ════════════════════════════════════════════════════════════════
    # HISTORY
    # ════════════════════════════════════════════════════════════════
    def _save_history(self, result: dict, A: list, b: list) -> None:
        record = {
            "type": "linear",
            "method": result.get("method", ""),
            "f_expr": None,
            "inputs": {
                "A": A,
                "b": b,
                "size": result.get("size", len(b)),
            },
            "result": {
                "root_or_solution": result.get("solution", []),
                "iterations_count": 0,
                "converged": True,
                "final_error": None,
            },
        }
        self.hm.save_record(record)
        self.controller.refresh_history_page()

    # ════════════════════════════════════════════════════════════════
    # PDF EXPORT
    # ════════════════════════════════════════════════════════════════
    def _export_pdf(self) -> None:
        if not self._last_result:
            return

        export_dir = self.sm.get("pdf_export_folder", "")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialdir=export_dir if export_dir else None,
            initialfile=f"linear_{self._last_result.get('method','').replace(' ','_')}.pdf",
            title="Save PDF Report",
        )
        if not filepath:
            return

        try:
            pdf_exporter.export_linear_pdf(
                filepath,
                self._last_result,
                self._last_inputs or {},
                settings=self.sm.all(),
            )
            self._show_success(f"✓  PDF saved: {filepath}")
        except ImportError as e:
            self._show_pdf_error(str(e))
        except Exception as e:
            self._show_pdf_error(str(e))

    # ════════════════════════════════════════════════════════════════
    # HELPERS
    # ════════════════════════════════════════════════════════════════
    def _clear(self) -> None:
        for row in self._matrix_entries:
            for e in row:
                e.delete(0, "end")
        for e in self._vector_entries:
            e.delete(0, "end")
        self._example_combo.set("-- Select example --")
        self._last_result = None
        self._last_inputs = None
        self._export_btn.configure(state="disabled")
        self._status_label.configure(
            text="Cleared. Fill the matrix and click Solve.",
            text_color=("#64748B", "#94A3B8"),
        )
        for w in (self._solution_card, self._steps_card, self._extra_card):
            w.grid_remove()
        if not self._placeholder.winfo_ismapped():
            self._placeholder.grid(row=10, column=0, pady=60)

    def _show_error(self, msg: str) -> None:
        self._status_label.configure(text=f"✕  {msg}", text_color=RED)

    def _show_success(self, msg: str) -> None:
        self._status_label.configure(text=msg, text_color=("#059669", "#34D399"))

    def _show_pdf_error(self, msg: str) -> None:
        win = ctk.CTkToplevel(self)
        win.title("PDF Export Error")
        win.geometry("500x180")
        win.grab_set()
        ctk.CTkLabel(win, text=msg, wraplength=460,
                     font=ctk.CTkFont(size=12)).pack(expand=True, padx=20, pady=20)
        ctk.CTkButton(win, text="OK", command=win.destroy, width=80).pack(pady=8)
