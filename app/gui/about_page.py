import customtkinter as ctk


BLUE   = "#2563EB"
PURPLE = "#7C3AED"
GREEN  = "#059669"
BG_CARD = ("white", "#1E293B")
BORDER  = ("#E2E8F0", "#334155")


class AboutPage(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller) -> None:
        super().__init__(parent, corner_radius=0, fg_color=("white", "#0F172A"))
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self) -> None:
        # Page title
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=36, pady=(32, 16))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            hdr, text="About  ·  Numerical Analysis Calculator",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"), anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            hdr, text="Open-source academic tool for numerical computation",
            font=ctk.CTkFont(size=13), text_color=("#64748B", "#94A3B8"), anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        ctk.CTkFrame(hdr, height=2, fg_color=BLUE, corner_radius=2
                     ).grid(row=2, column=0, sticky="ew", pady=(12, 0))

        row = 1
        # ── Project card ─────────────────────────────────────────────
        row = self._info_card(row, "📋  Project Overview",
            "Numerical Analysis Calculator is an open-source Python desktop application "
            "designed to solve numerical analysis problems with precision and efficiency. "
            "Built for students, educators, engineers, and researchers who need reliable, "
            "visual, and well-documented numerical computation tools.\n\n"
            "The application separates the GUI layer cleanly from the computation layer, "
            "using SymPy for safe mathematical expression parsing, NumPy for matrix "
            "operations, and Matplotlib for interactive visualization.",
            color=BLUE)

        # ── Methods card ─────────────────────────────────────────────
        row = self._methods_card(row)

        # ── Libraries card ───────────────────────────────────────────
        row = self._libraries_card(row)

        # ── Academic note ────────────────────────────────────────────
        row = self._info_card(row, "🎓  Academic & Open-Source Purpose",
            "This application is developed for educational and research purposes. "
            "All numerical methods are implemented from first principles with clear "
            "step-by-step output, making the algorithms transparent and understandable.\n\n"
            "The source code is freely available for modification and learning. "
            "Contributions, bug reports, and suggestions are welcome.",
            color=GREEN)

        # ── Version footer ───────────────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=row, column=0, pady=(8, 32))
        ctk.CTkLabel(
            footer,
            text="Numerical Analysis Calculator  •  Version 1.0.0  •  Python 3.10+",
            font=ctk.CTkFont(size=11),
            text_color=("#94A3B8", "#64748B"),
        ).pack()

    def _card_frame(self, row: int, color: str = BLUE) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self, corner_radius=12, fg_color=BG_CARD,
            border_width=1, border_color=BORDER,
        )
        card.grid(row=row, column=0, sticky="ew", padx=36, pady=6)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=0
                     ).grid(row=0, column=0, sticky="ew")
        return card

    def _info_card(self, row: int, title: str, body: str, color: str = BLUE) -> int:
        card = self._card_frame(row, color)
        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"), anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(14, 4))
        ctk.CTkLabel(
            card, text=body,
            font=ctk.CTkFont(size=12),
            text_color=("#475569", "#94A3B8"),
            wraplength=700, justify="left", anchor="nw",
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
        return row + 1

    def _methods_card(self, row: int) -> int:
        card = self._card_frame(row, PURPLE)
        ctk.CTkLabel(
            card, text="🔢  Supported Numerical Methods",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"), anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(14, 8))

        cols = ctk.CTkFrame(card, fg_color="transparent")
        cols.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
        cols.grid_columnconfigure((0, 1), weight=1)

        nl_methods = [
            ("Bisection", "Bracket method — midpoint bisection"),
            ("False Position", "Bracket method — linear interpolation"),
            ("Newton-Raphson", "Tangent line — symbolic derivative"),
            ("Secant", "Two-point approximation"),
            ("Fixed Point", "Iterative g(x) convergence"),
        ]
        lin_methods = [
            ("Gauss Elimination", "Partial pivoting + back substitution"),
            ("LU Decomposition", "Doolittle factorization (L·U = A)"),
            ("Gauss-Jordan", "Full RREF reduction"),
            ("Cramer's Rule", "Determinant-based solution"),
        ]

        def method_block(parent, col, heading, items):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=0, column=col, sticky="nw", padx=8)
            ctk.CTkLabel(
                f, text=heading,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#374151", "#CBD5E1"),
            ).pack(anchor="w", pady=(0, 6))
            for name, desc in items:
                row_f = ctk.CTkFrame(f, fg_color="transparent")
                row_f.pack(fill="x", pady=2)
                ctk.CTkLabel(row_f, text="▸ " + name,
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=("#1E293B", "#F1F5F9")).pack(anchor="w")
                ctk.CTkLabel(row_f, text="   " + desc,
                             font=ctk.CTkFont(size=11),
                             text_color=("#64748B", "#94A3B8")).pack(anchor="w")

        method_block(cols, 0, "Non-Linear Equations", nl_methods)
        method_block(cols, 1, "Linear Systems", lin_methods)
        return row + 1

    def _libraries_card(self, row: int) -> int:
        card = self._card_frame(row, "#059669")
        ctk.CTkLabel(
            card, text="📦  Libraries & Dependencies",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"), anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(14, 8))

        libraries = [
            ("CustomTkinter", "Modern themed GUI widgets for Python"),
            ("NumPy",         "High-performance matrix and array operations"),
            ("SymPy",         "Symbolic math — safe expression parsing and differentiation"),
            ("SciPy",         "Scientific computing utilities"),
            ("Matplotlib",    "Embedded interactive graphs with Tkinter backend"),
            ("ReportLab",     "Professional PDF report generation with tables and images"),
            ("Pillow",        "Image processing for figure embedding in PDFs"),
        ]
        tbl = ctk.CTkFrame(card, fg_color="transparent")
        tbl.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
        tbl.grid_columnconfigure(1, weight=1)

        for i, (lib, desc) in enumerate(libraries):
            bg = ("white", "#1E293B") if i % 2 == 0 else ("#F8FAFC", "#0F172A")
            row_f = ctk.CTkFrame(tbl, fg_color=bg, corner_radius=6)
            row_f.grid(row=i, column=0, columnspan=2, sticky="ew", pady=1)
            row_f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row_f, text=lib,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=("#2563EB", "#93C5FD"),
                         width=130, anchor="w"
                         ).grid(row=0, column=0, padx=(12, 8), pady=5, sticky="w")
            ctk.CTkLabel(row_f, text=desc,
                         font=ctk.CTkFont(size=11),
                         text_color=("#475569", "#94A3B8"), anchor="w"
                         ).grid(row=0, column=1, padx=4, pady=5, sticky="w")
        return row + 1
