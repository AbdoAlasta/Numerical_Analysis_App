import customtkinter as ctk
from typing import Callable


NAV_ITEMS = [
    ("Home",                "home"),
    ("Non-Linear Equations","nonlinear"),
    ("Linear Systems",      "linear"),
    ("History",             "history"),
    ("Settings",            "settings"),
    ("About",               "about"),
]

SIDEBAR_BG   = "#1E293B"
ACTIVE_COLOR = "#2563EB"
HOVER_COLOR  = "#334155"
TEXT_COLOR   = "#F1F5F9"
MUTED_COLOR  = "#94A3B8"


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback: Callable[[str], None]) -> None:
        super().__init__(parent, width=220, corner_radius=0, fg_color=SIDEBAR_BG)
        self.navigate_callback = navigate_callback
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        self.grid_propagate(False)
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)

        # ── Title block ──────────────────────────────────────────────
        title_frame = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, corner_radius=0)
        title_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        ctk.CTkLabel(
            title_frame,
            text="⬡  Numerical\n     Analysis",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=TEXT_COLOR,
            justify="left",
        ).pack(side="top", padx=18, pady=(22, 4), anchor="w")

        # Blue accent line
        ctk.CTkFrame(
            title_frame, height=2, fg_color=ACTIVE_COLOR, corner_radius=0
        ).pack(fill="x", padx=18, pady=(0, 14))

        # ── Navigation ───────────────────────────────────────────────
        nav_frame = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, corner_radius=0)
        nav_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        ctk.CTkLabel(
            nav_frame,
            text="MENU",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=MUTED_COLOR,
        ).pack(anchor="w", padx=20, pady=(4, 6))

        for label, key in NAV_ITEMS:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"  {label}",
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                hover_color=HOVER_COLOR,
                text_color=TEXT_COLOR,
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self.navigate_callback(k),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[key] = btn

        # ── Footer ───────────────────────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, corner_radius=0)
        footer.grid(row=2, column=0, sticky="ew")

        ctk.CTkFrame(
            footer, height=1, fg_color="#334155", corner_radius=0
        ).pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            footer,
            text="Numerical Analysis Calculator\nv1.0.0  •  Open Source",
            font=ctk.CTkFont(size=9),
            text_color=MUTED_COLOR,
            justify="center",
        ).pack(pady=(0, 14))

    def set_active(self, page_name: str) -> None:
        for key, btn in self.nav_buttons.items():
            if key == page_name:
                btn.configure(fg_color=ACTIVE_COLOR, text_color="white",
                               font=ctk.CTkFont(size=13, weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_COLOR,
                               font=ctk.CTkFont(size=13))
