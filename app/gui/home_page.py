import customtkinter as ctk


BLUE   = "#2563EB"
PURPLE = "#7C3AED"
GREEN  = "#059669"
BG_CARD = ("white", "#1E293B")
BORDER  = ("#E2E8F0", "#334155")


class HomePage(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller) -> None:
        super().__init__(parent, corner_radius=0, fg_color=("white", "#0F172A"))
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self._build_header()
        self._build_cards()
        self._build_footer()

    # ── Header ────────────────────────────────────────────────────────
    def _build_header(self) -> None:
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=40, pady=(36, 20))
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr,
            text="Numerical Analysis Calculator",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
            anchor="center",
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            hdr,
            text="Solve non-linear equations and linear systems with precision and step-by-step clarity",
            font=ctk.CTkFont(size=13),
            text_color=("#64748B", "#94A3B8"),
            anchor="center",
        ).grid(row=1, column=0, sticky="ew", pady=(4, 0))

        ctk.CTkFrame(hdr, height=2, fg_color=BLUE, corner_radius=2
                     ).grid(row=2, column=0, sticky="ew", pady=(14, 0), padx=80)

    # ── Solver Cards ──────────────────────────────────────────────────
    def _build_cards(self) -> None:
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=8)
        cards_frame.grid_columnconfigure((0, 1), weight=1)

        self._solver_card(
            cards_frame, col=0,
            icon="📐",
            title="Non-Linear Equations",
            color=BLUE,
            badge_text="5 Methods",
            description=(
                "Find roots of complex functions using iterative methods.\n\n"
                "• Bisection Method\n"
                "• False Position Method\n"
                "• Newton-Raphson Method\n"
                "• Secant Method\n"
                "• Fixed Point Iteration"
            ),
            btn_text="Open Solver",
            btn_command=lambda: self.controller.show_page("nonlinear"),
            btn_color=BLUE,
        )
        self._solver_card(
            cards_frame, col=1,
            icon="🧮",
            title="Linear Systems",
            color=PURPLE,
            badge_text="4 Methods",
            description=(
                "Solve systems of linear equations with full step-by-step solutions.\n\n"
                "• Gauss Elimination\n"
                "• LU Decomposition\n"
                "• Gauss-Jordan Method\n"
                "• Cramer's Rule"
            ),
            btn_text="Open Solver",
            btn_command=lambda: self.controller.show_page("linear"),
            btn_color=PURPLE,
        )

    def _solver_card(self, parent, col: int, icon: str, title: str, color: str,
                     badge_text: str, description: str, btn_text: str,
                     btn_command, btn_color: str) -> None:
        card = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BORDER,
        )
        card.grid(row=0, column=col, sticky="nsew", padx=10, pady=6)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(3, weight=1)

        # Colored top accent bar
        ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=0
                     ).grid(row=0, column=0, sticky="ew")

        # Header row
        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.grid(row=1, column=0, sticky="ew", padx=20, pady=(16, 4))
        header_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_row,
            text=f"{icon}  {title}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1E293B", "#F1F5F9"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        badge = ctk.CTkLabel(
            header_row,
            text=badge_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white",
            fg_color=color,
            corner_radius=8,
            padx=8,
            pady=2,
        )
        badge.grid(row=0, column=1, sticky="e")

        # Description
        ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color=("#475569", "#94A3B8"),
            justify="left",
            anchor="nw",
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(6, 12))

        # Button
        ctk.CTkButton(
            card,
            text=btn_text,
            fg_color=btn_color,
            hover_color=_darken(btn_color),
            corner_radius=8,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=btn_command,
        ).grid(row=3, column=0, sticky="ew", padx=20, pady=(4, 20))

    # ── Footer info ───────────────────────────────────────────────────
    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color=("white", "#1E293B"),
                              corner_radius=12, border_width=1, border_color=BORDER)
        footer.grid(row=2, column=0, sticky="ew", padx=40, pady=(16, 32))
        footer.grid_columnconfigure((0, 1, 2), weight=1)

        features = [
            ("📊", "Interactive Graphs", "Visualize function behavior\nwith Matplotlib"),
            ("📄", "PDF Export", "Export results with tables\nand figures"),
            ("🕓", "History Tracking", "Automatically save and\nreview past solutions"),
        ]
        for i, (icon, title, desc) in enumerate(features):
            f = ctk.CTkFrame(footer, fg_color="transparent")
            f.grid(row=0, column=i, padx=20, pady=16, sticky="n")
            ctk.CTkLabel(f, text=icon, font=ctk.CTkFont(size=22)).pack()
            ctk.CTkLabel(f, text=title,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=("#1E293B", "#F1F5F9")).pack(pady=(4, 2))
            ctk.CTkLabel(f, text=desc,
                         font=ctk.CTkFont(size=11),
                         text_color=("#64748B", "#94A3B8"),
                         justify="center").pack()


def _darken(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = max(0, int(r * 0.80))
    g = max(0, int(g * 0.80))
    b = max(0, int(b * 0.80))
    return f"#{r:02X}{g:02X}{b:02X}"
