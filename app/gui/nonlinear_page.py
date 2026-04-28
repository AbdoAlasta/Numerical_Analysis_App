"""Non-linear equation solver page.
Left panel: all inputs (scrollable, 390px).
Right panel: results — iteration table, summary, graph, export.
"""
import math
from tkinter import ttk, filedialog
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from app.services.settings_manager import SettingsManager
from app.services.history_manager import HistoryManager
from app.methods import nonlinear as nl
from app.utils import validators, plotting
from app.services import pdf_exporter


BLUE   = "#2563EB"
PURPLE = "#7C3AED"
GREEN  = "#059669"
RED    = "#EF4444"
BG_CARD = ("white", "#1E293B")
BORDER  = ("#E2E8F0", "#334155")

METHODS = ["Bisection", "False Position", "Fixed Point", "Newton-Raphson", "Secant"]

EXAMPLE_FUNCTIONS = [
    "-2 + 7*x - 5*x**2 + 6*x**3",
    "x**3 - x - 2",
    "x**2 - 4",
    "cos(x) - x",
    "exp(-x) - x",
    "sin(x) - x/2",
    "x**3 - 2*x - 5",
]

# Column definitions: (display_header, dict_key)
COLUMNS = {
    "Bisection": [
        ("n",     "n"),
        ("xl",    "xl"),
        ("f(xl)", "f_xl"),
        ("xu",    "xu"),
        ("f(xu)", "f_xu"),
        ("xr",    "xr"),
        ("f(xr)", "f_xr"),
        ("ea(%)", "ea"),
    ],
    "False Position": [
        ("n",     "n"),
        ("xl",    "xl"),
        ("f(xl)", "f_xl"),
        ("xu",    "xu"),
        ("f(xu)", "f_xu"),
        ("xr",    "xr"),
        ("f(xr)", "f_xr"),
        ("ea(%)", "ea"),
    ],
    "Newton-Raphson": [
        ("n",      "n"),
        ("xi",     "xi"),
        ("f(xi)",  "f_xi"),
        ("f'(xi)", "df_xi"),
        ("xi+1",   "xi_next"),
        ("ea(%)",  "ea"),
    ],
    "Secant": [
        ("n",        "n"),
        ("xi-1",     "xi_prev"),
        ("xi",       "xi"),
        ("f(xi-1)",  "f_xi_prev"),
        ("f(xi)",    "f_xi"),
        ("xi+1",     "xi_next"),
        ("ea(%)",    "ea"),
    ],
    "Fixed Point": [
        ("n",     "n"),
        ("xi",    "xi"),
        ("g(xi)", "g_xi"),
        ("ea(%)", "ea"),
    ],
}


class NonLinearPage(ctk.CTkFrame):
    def __init__(self, parent, controller,
                 settings_manager: SettingsManager,
                 history_manager: HistoryManager) -> None:
        super().__init__(parent, corner_radius=0, fg_color=("white", "#0F172A"))
        self.controller = controller
        self.sm = settings_manager
        self.hm = history_manager

        self._current_fig = None
        self._current_canvas = None
        self._last_result: dict | None = None
        self._last_inputs: dict | None = None

        self.grid_columnconfigure(0, weight=0, minsize=390)
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

        r = 0

        # ── Title ──────────────────────────────────────────────────
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.grid(row=r, column=0, sticky="ew", padx=16, pady=(20, 4))
        ctk.CTkLabel(
            title_frame,
            text="Non-Linear Equations Solver",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"), anchor="w",
        ).pack(anchor="w")
        ctk.CTkFrame(title_frame, height=2, fg_color=BLUE, corner_radius=2
                     ).pack(fill="x", pady=(6, 0))
        r += 1

        # ── f(x) ───────────────────────────────────────────────────
        ctk.CTkLabel(left, text="Function  f(x)",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=("#374151", "#CBD5E1"), anchor="w",
                     ).grid(row=r, column=0, sticky="w", padx=16, pady=(12, 2))
        r += 1
        self._fx_entry = ctk.CTkEntry(
            left, placeholder_text="e.g.  x**3 - x - 2", height=34,
        )
        self._fx_entry.grid(row=r, column=0, sticky="ew", padx=16, pady=(0, 4))
        r += 1

        # Examples dropdown
        ctk.CTkLabel(left, text="Load example",
                     font=ctk.CTkFont(size=10), text_color=("#94A3B8", "#64748B"),
                     anchor="w").grid(row=r, column=0, sticky="w", padx=16)
        r += 1
        self._example_combo = ctk.CTkComboBox(
            left, values=EXAMPLE_FUNCTIONS, width=340,
            command=self._on_example_selected,
        )
        self._example_combo.set("-- Select example function --")
        self._example_combo.grid(row=r, column=0, sticky="ew", padx=16, pady=(0, 8))
        r += 1

        # ── Method ─────────────────────────────────────────────────
        ctk.CTkLabel(left, text="Method",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=("#374151", "#CBD5E1"), anchor="w",
                     ).grid(row=r, column=0, sticky="w", padx=16, pady=(4, 2))
        r += 1
        self._method_combo = ctk.CTkComboBox(
            left, values=METHODS,
            command=self._on_method_changed, width=340,
        )
        default_method = self.sm.get("default_nonlinear_method", "Bisection")
        self._method_combo.set(default_method)
        self._method_combo.grid(row=r, column=0, sticky="ew", padx=16, pady=(0, 8))
        r += 1

        # ── Dynamic parameter frames (created once, shown/hidden) ──
        # Container for all parameter frames
        self._param_container = ctk.CTkFrame(left, fg_color="transparent")
        self._param_container.grid(row=r, column=0, sticky="ew", padx=0)
        self._param_container.grid_columnconfigure(0, weight=1)
        r += 1

        self._param_frames: dict[str, ctk.CTkFrame] = {}
        self._entries: dict[str, ctk.CTkEntry] = {}

        # Bracket frame (xl, xu) — Bisection & False Position
        self._param_frames["bracket"] = self._make_param_frame(
            self._param_container,
            [("Lower bound  xl", "xl", "e.g. 1"),
             ("Upper bound  xu", "xu", "e.g. 2")],
        )

        # x0 frame — Newton-Raphson, Fixed Point, Secant (first point)
        self._param_frames["x0"] = self._make_param_frame(
            self._param_container,
            [("Initial guess  x0", "x0", "e.g. 1.5")],
        )

        # x1 frame — Secant second point
        self._param_frames["x1"] = self._make_param_frame(
            self._param_container,
            [("Second initial guess  x1", "x1", "e.g. 2.0")],
        )

        # g(x) frame — Fixed Point
        self._param_frames["gx"] = self._make_param_frame(
            self._param_container,
            [],  # label/entry added manually below
        )
        ctk.CTkLabel(
            self._param_frames["gx"],
            text="g(x) iteration function",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#374151", "#CBD5E1"), anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(4, 2))
        gx_entry = ctk.CTkEntry(
            self._param_frames["gx"],
            placeholder_text="e.g.  (x + 2)**(1/3)", height=34,
        )
        gx_entry.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 6))
        self._entries["g_expr"] = gx_entry

        # Show initial frames
        self._on_method_changed(default_method)

        # ── Solver parameters ──────────────────────────────────────
        params_frame = ctk.CTkFrame(left, fg_color="transparent")
        params_frame.grid(row=r, column=0, sticky="ew", padx=0)
        params_frame.grid_columnconfigure((0, 1), weight=1)
        r += 1

        def param_entry(parent, row, col, label, key, default="", width=130):
            ctk.CTkLabel(parent, text=label,
                         font=ctk.CTkFont(size=11),
                         text_color=("#374151", "#CBD5E1"), anchor="w",
                         ).grid(row=row * 2, column=col, sticky="w", padx=16, pady=(6, 2))
            e = ctk.CTkEntry(parent, height=32, width=width)
            e.insert(0, str(default))
            e.grid(row=row * 2 + 1, column=col, sticky="ew", padx=16, pady=(0, 4))
            self._entries[key] = e

        param_entry(params_frame, 0, 0, "Epsilon (tolerance)", "epsilon",
                    str(self.sm.get("default_epsilon", "0.0001")))
        param_entry(params_frame, 0, 1, "Max iterations", "max_iter",
                    str(self.sm.get("default_max_iter", "100")))

        # Decimal places & round
        dp_frame = ctk.CTkFrame(left, fg_color="transparent")
        dp_frame.grid(row=r, column=0, sticky="ew", padx=0)
        dp_frame.grid_columnconfigure((0, 1), weight=1)
        r += 1

        ctk.CTkLabel(dp_frame, text="Decimal places",
                     font=ctk.CTkFont(size=11),
                     text_color=("#374151", "#CBD5E1"), anchor="w",
                     ).grid(row=0, column=0, sticky="w", padx=16, pady=(6, 2))
        self._dp_combo = ctk.CTkComboBox(
            dp_frame, values=["2", "3", "4", "5", "6", "8", "10"],
            width=120,
        )
        dp_default = str(self.sm.get("default_decimal_places", "6"))
        self._dp_combo.set(dp_default)
        self._dp_combo.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 4))

        self._round_var = ctk.BooleanVar(value=self.sm.get("enable_rounding", False))
        ctk.CTkCheckBox(
            dp_frame, text="Round result",
            variable=self._round_var,
        ).grid(row=1, column=1, sticky="w", padx=8, pady=(0, 4))

        # ── Stop condition ─────────────────────────────────────────
        ctk.CTkLabel(left, text="Stop Condition",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=("#374151", "#CBD5E1"), anchor="w",
                     ).grid(row=r, column=0, sticky="w", padx=16, pady=(8, 4))
        r += 1
        stop_frame = ctk.CTkFrame(left, fg_color="transparent")
        stop_frame.grid(row=r, column=0, sticky="ew", padx=16)
        r += 1
        stop_cond = self.sm.get("default_stop_condition", "epsilon")
        self._stop_var = ctk.IntVar(value=0 if stop_cond == "epsilon" else 1)
        ctk.CTkRadioButton(
            stop_frame, text="Stop by epsilon (tolerance)",
            variable=self._stop_var, value=0,
        ).pack(anchor="w", pady=2)
        ctk.CTkRadioButton(
            stop_frame, text="Stop by max iterations",
            variable=self._stop_var, value=1,
        ).pack(anchor="w", pady=2)

        # ── Buttons ────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(left, fg_color="transparent")
        btn_frame.grid(row=r, column=0, sticky="ew", padx=16, pady=(14, 20))
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        r += 1

        ctk.CTkButton(
            btn_frame, text="▶  Solve",
            fg_color=BLUE, hover_color="#1D4ED8",
            height=40, font=ctk.CTkFont(size=13, weight="bold"),
            command=self._solve,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            btn_frame, text="✕  Clear",
            fg_color="#64748B", hover_color="#475569",
            height=40, font=ctk.CTkFont(size=13),
            command=self._clear,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _make_param_frame(self, parent, fields: list) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        for i, (label, key, placeholder) in enumerate(fields):
            ctk.CTkLabel(frame, text=label,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=("#374151", "#CBD5E1"), anchor="w",
                         ).grid(row=i * 2, column=0, sticky="w", padx=16, pady=(4, 2))
            entry = ctk.CTkEntry(frame, placeholder_text=placeholder, height=34)
            entry.grid(row=i * 2 + 1, column=0, sticky="ew", padx=16, pady=(0, 6))
            self._entries[key] = entry
        return frame

    def _on_method_changed(self, method: str) -> None:
        for frame in self._param_frames.values():
            frame.grid_remove()

        if method in ("Bisection", "False Position"):
            self._param_frames["bracket"].grid(row=0, column=0, sticky="ew")
        elif method == "Newton-Raphson":
            self._param_frames["x0"].grid(row=0, column=0, sticky="ew")
        elif method == "Secant":
            self._param_frames["x0"].grid(row=0, column=0, sticky="ew")
            self._param_frames["x1"].grid(row=1, column=0, sticky="ew")
        elif method == "Fixed Point":
            self._param_frames["x0"].grid(row=0, column=0, sticky="ew")
            self._param_frames["gx"].grid(row=1, column=0, sticky="ew")

    def _on_example_selected(self, value: str) -> None:
        if value.startswith("--"):
            return
        self._fx_entry.delete(0, "end")
        self._fx_entry.insert(0, value)

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

        # Status label
        self._status_label = ctk.CTkLabel(
            bar, text="Enter a function and click Solve.",
            font=ctk.CTkFont(size=11),
            text_color=("#64748B", "#94A3B8"),
        )
        self._status_label.grid(row=0, column=2, padx=12, sticky="w")

        # Scrollable results area
        self._results_scroll = ctk.CTkScrollableFrame(
            right, corner_radius=0, fg_color="transparent",
        )
        self._results_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self._results_scroll.grid_columnconfigure(0, weight=1)

        # Summary card (hidden initially)
        self._summary_card = ctk.CTkFrame(
            self._results_scroll,
            corner_radius=12, fg_color=BG_CARD,
            border_width=1, border_color=BORDER,
        )

        # Table frame
        self._table_frame = ctk.CTkFrame(
            self._results_scroll,
            corner_radius=12, fg_color=BG_CARD,
            border_width=1, border_color=BORDER,
        )

        # Graph frame
        self._graph_frame = ctk.CTkFrame(
            self._results_scroll,
            corner_radius=12, fg_color=BG_CARD,
            border_width=1, border_color=BORDER,
        )

        self._placeholder_label = ctk.CTkLabel(
            self._results_scroll,
            text="No results yet.\nEnter parameters and click  ▶ Solve",
            font=ctk.CTkFont(size=13),
            text_color=("#94A3B8", "#64748B"),
        )
        self._placeholder_label.grid(row=10, column=0, pady=60)

    # ════════════════════════════════════════════════════════════════
    # SOLVE
    # ════════════════════════════════════════════════════════════════
    def _collect_inputs(self) -> dict | None:
        method = self._method_combo.get()
        f_expr  = self._fx_entry.get().strip()
        epsilon = self._entries["epsilon"].get().strip()
        max_iter = self._entries["max_iter"].get().strip()
        dp = self._dp_combo.get().strip()

        params = {
            "epsilon": epsilon,
            "max_iter": max_iter,
        }
        if method in ("Bisection", "False Position"):
            params["xl"] = self._entries["xl"].get().strip()
            params["xu"] = self._entries["xu"].get().strip()
        elif method == "Newton-Raphson":
            params["x0"] = self._entries["x0"].get().strip()
        elif method == "Secant":
            params["x0"] = self._entries["x0"].get().strip()
            params["x1"] = self._entries["x1"].get().strip()
        elif method == "Fixed Point":
            params["x0"] = self._entries["x0"].get().strip()
            params["g_expr"] = self._entries["g_expr"].get().strip()

        ok, msg = validators.validate_nonlinear_inputs(method, f_expr, params)
        if not ok:
            self._show_error(msg)
            return None

        return {
            "method": method,
            "f_expr": f_expr,
            "params": params,
            "decimal_places": int(dp) if dp.isdigit() else 6,
            "stop_by_epsilon": (self._stop_var.get() == 0),
        }

    def _solve(self) -> None:
        inputs = self._collect_inputs()
        if inputs is None:
            return

        method = inputs["method"]
        f_expr = inputs["f_expr"]
        params = inputs["params"]
        dp = inputs["decimal_places"]
        stop_by_eps = inputs["stop_by_epsilon"]
        epsilon = float(params["epsilon"])
        max_iter = int(float(params["max_iter"]))

        try:
            if method == "Bisection":
                result = nl.solve_bisection(
                    f_expr, float(params["xl"]), float(params["xu"]),
                    epsilon, max_iter, dp, stop_by_eps)
            elif method == "False Position":
                result = nl.solve_false_position(
                    f_expr, float(params["xl"]), float(params["xu"]),
                    epsilon, max_iter, dp, stop_by_eps)
            elif method == "Newton-Raphson":
                result = nl.solve_newton_raphson(
                    f_expr, float(params["x0"]),
                    epsilon, max_iter, dp, stop_by_eps)
            elif method == "Secant":
                result = nl.solve_secant(
                    f_expr, float(params["x0"]), float(params["x1"]),
                    epsilon, max_iter, dp, stop_by_eps)
            elif method == "Fixed Point":
                result = nl.solve_fixed_point(
                    f_expr, params["g_expr"], float(params["x0"]),
                    epsilon, max_iter, dp, stop_by_eps)
            else:
                self._show_error(f"Unknown method: {method}")
                return
        except Exception as exc:
            self._show_error(str(exc))
            return

        self._last_result = result
        self._last_inputs = {
            "f_expr": f_expr,
            **{k: v for k, v in params.items()},
            "decimal_places": dp,
            "stop_by_epsilon": stop_by_eps,
        }
        self._display_results(result)

        # Auto-save history
        if self.sm.get("auto_save_results", True):
            self._save_history(result, self._last_inputs)

    def _display_results(self, result: dict) -> None:
        self._placeholder_label.grid_remove()
        self._show_success(
            f"✓  Root ≈ {result['root']}  |  {result['iterations_count']} iterations  |  "
            f"{'Converged' if result['converged'] else 'Did not converge'}"
        )
        self._populate_summary(result)
        self._populate_table(result)

        # Graph
        f_expr  = result.get("f_expr", "")
        root    = result.get("root")
        method  = result.get("method", "")
        xl = None
        xu = None
        if self._last_inputs:
            xl = self._last_inputs.get("xl")
            xu = self._last_inputs.get("xu")
            if xl: xl = float(xl)
            if xu: xu = float(xu)

        try:
            fig = plotting.create_nonlinear_figure(
                f_expr, float(root), xl, xu, method,
                title=f"{method}  —  f(x) = {f_expr}",
            )
            self._embed_graph(fig)
        except Exception:
            pass

        self._export_btn.configure(state="normal")

    def _populate_summary(self, result: dict) -> None:
        for w in self._summary_card.winfo_children():
            w.destroy()

        ctk.CTkFrame(self._summary_card, height=3, fg_color=GREEN, corner_radius=0
                     ).grid(row=0, column=0, columnspan=4, sticky="ew")
        ctk.CTkLabel(
            self._summary_card, text="Solution Summary",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
        ).grid(row=1, column=0, columnspan=4, sticky="w", padx=16, pady=(10, 8))

        items = [
            ("Root  x*",      str(result.get("root", "N/A"))),
            ("Iterations",    str(result.get("iterations_count", "N/A"))),
            ("Final Error %", str(result.get("final_error", "N/A"))),
            ("Converged",     "Yes ✓" if result.get("converged") else "No ✗"),
        ]
        for col, (label, value) in enumerate(items):
            f = ctk.CTkFrame(self._summary_card, fg_color=("white", "#0F172A"),
                             corner_radius=8)
            f.grid(row=2, column=col, padx=8, pady=(0, 14), sticky="nsew")
            self._summary_card.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(f, text=label,
                         font=ctk.CTkFont(size=10),
                         text_color=("#64748B", "#94A3B8")).pack(pady=(8, 2))
            color = "#059669" if (label == "Converged" and "Yes" in value) else \
                    "#EF4444" if (label == "Converged") else BLUE
            ctk.CTkLabel(f, text=value,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=color).pack(pady=(0, 8))

        self._summary_card.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))

    def _populate_table(self, result: dict) -> None:
        method = result.get("method", "Bisection")
        iterations = result.get("iterations", [])
        col_defs = COLUMNS.get(method, [])

        for w in self._table_frame.winfo_children():
            w.destroy()

        ctk.CTkFrame(self._table_frame, height=3, fg_color=BLUE, corner_radius=0
                     ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            self._table_frame,
            text=f"Iteration Table  —  {method}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(10, 6))

        tv_frame = ctk.CTkFrame(self._table_frame, fg_color="transparent")
        tv_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))

        headers  = [h for h, _ in col_defs]
        keys     = [k for _, k in col_defs]
        col_widths = max(60, int(500 / max(len(headers), 1)))

        tv = ttk.Treeview(
            tv_frame,
            columns=headers,
            show="headings",
            height=min(len(iterations), 14),
        )
        for h in headers:
            tv.heading(h, text=h)
            tv.column(h, width=col_widths, anchor="center", minwidth=50)

        for row in iterations:
            tv.insert("", "end", values=[str(row.get(k, "")) for k in keys])

        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=tv.yview)
        hsb = ttk.Scrollbar(tv_frame, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tv.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tv_frame.grid_rowconfigure(0, weight=1)
        tv_frame.grid_columnconfigure(0, weight=1)

        self._table_frame.grid_columnconfigure(0, weight=1)
        self._table_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=6)

    def _embed_graph(self, fig) -> None:
        if self._current_canvas is not None:
            try:
                self._current_canvas.get_tk_widget().destroy()
            except Exception:
                pass
        if self._current_fig is not None:
            try:
                plt.close(self._current_fig)
            except Exception:
                pass

        for w in self._graph_frame.winfo_children():
            w.destroy()

        ctk.CTkFrame(self._graph_frame, height=3, fg_color=PURPLE, corner_radius=0
                     ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            self._graph_frame, text="Function Graph",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(10, 4))

        canvas_holder = ctk.CTkFrame(self._graph_frame, fg_color="transparent")
        canvas_holder.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))

        canvas = FigureCanvasTkAgg(fig, master=canvas_holder)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self._current_fig = fig
        self._current_canvas = canvas
        self._graph_frame.grid_columnconfigure(0, weight=1)
        self._graph_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=6)

    # ════════════════════════════════════════════════════════════════
    # HISTORY
    # ════════════════════════════════════════════════════════════════
    def _save_history(self, result: dict, inputs: dict) -> None:
        sol = result.get("root")
        try:
            sol_val = float(sol) if sol is not None else None
        except Exception:
            sol_val = sol

        record = {
            "type": "nonlinear",
            "method": result.get("method", ""),
            "f_expr": result.get("f_expr", ""),
            "inputs": {k: str(v) for k, v in inputs.items()},
            "result": {
                "root_or_solution": sol_val,
                "iterations_count": result.get("iterations_count", 0),
                "converged": result.get("converged", False),
                "final_error": result.get("final_error"),
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
            initialfile=f"nonlinear_{self._last_result.get('method', '').replace(' ', '_')}.pdf",
            title="Save PDF Report",
        )
        if not filepath:
            return

        try:
            pdf_exporter.export_nonlinear_pdf(
                filepath,
                self._last_result,
                self._last_inputs or {},
                fig=self._current_fig,
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
        self._fx_entry.delete(0, "end")
        for key, entry in self._entries.items():
            if key not in ("epsilon", "max_iter"):
                entry.delete(0, "end")
        self._example_combo.set("-- Select example function --")
        self._last_result = None
        self._last_inputs = None
        self._export_btn.configure(state="disabled")
        self._status_label.configure(
            text="Cleared. Enter parameters and click Solve.",
            text_color=("#64748B", "#94A3B8"),
        )
        # Hide result sections
        for w in (self._summary_card, self._table_frame, self._graph_frame):
            w.grid_remove()
        if not self._placeholder_label.winfo_ismapped():
            self._placeholder_label.grid(row=10, column=0, pady=60)

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
