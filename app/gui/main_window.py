import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from app.gui.sidebar import Sidebar
from app.services.settings_manager import SettingsManager
from app.services.history_manager import HistoryManager


class MainWindow(ctk.CTk):
    def __init__(self, settings_manager: SettingsManager,
                 history_manager: HistoryManager) -> None:
        super().__init__()
        self.settings_manager = settings_manager
        self.history_manager = history_manager

        self.title("Numerical Analysis Calculator")
        self.geometry("1280x780")
        self.minsize(1050, 680)

        self._apply_treeview_style()
        self._build_layout()
        self._build_pages()
        self.show_page("home")

    # ── Layout ────────────────────────────────────────────────────────
    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=0, minsize=220)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, navigate_callback=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_frame = ctk.CTkFrame(self, corner_radius=0,
                                          fg_color=("white", "#0F172A"))
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _build_pages(self) -> None:
        # Import here to avoid circular imports at module load time
        from app.gui.home_page import HomePage
        from app.gui.nonlinear_page import NonLinearPage
        from app.gui.linear_page import LinearPage
        from app.gui.history_page import HistoryPage
        from app.gui.settings_page import SettingsPage
        from app.gui.about_page import AboutPage

        self.pages: dict[str, ctk.CTkFrame] = {}

        def make(cls, *extra_args):
            page = cls(self.content_frame, self, *extra_args)
            page.grid(row=0, column=0, sticky="nsew")
            return page

        self.pages["home"]      = make(HomePage)
        self.pages["nonlinear"] = make(NonLinearPage,
                                       self.settings_manager, self.history_manager)
        self.pages["linear"]    = make(LinearPage,
                                       self.settings_manager, self.history_manager)
        self.pages["history"]   = make(HistoryPage, self.history_manager)
        self.pages["settings"]  = make(SettingsPage, self.settings_manager)
        self.pages["about"]     = make(AboutPage)

        for page in self.pages.values():
            page.grid_remove()

    # ── Navigation ────────────────────────────────────────────────────
    def show_page(self, page_name: str) -> None:
        for page in self.pages.values():
            page.grid_remove()
        if page_name in self.pages:
            self.pages[page_name].grid()
            self.sidebar.set_active(page_name)

    def refresh_history_page(self) -> None:
        history_page = self.pages.get("history")
        if history_page and hasattr(history_page, "refresh"):
            history_page.refresh()

    # ── Theme ──────────────────────────────────────────────────────────
    def apply_theme(self, mode: str) -> None:
        ctk.set_appearance_mode(mode)
        self.settings_manager.set("appearance_mode", mode.lower())
        self._apply_treeview_style()
        self.content_frame.configure(
            fg_color=("white", "#0F172A")
        )

    def _apply_treeview_style(self) -> None:
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        style = ttk.Style(self)
        style.theme_use("default")
        if is_dark:
            bg   = "#1E293B"
            fg   = "#F1F5F9"
            sel  = "#2563EB"
            hdr  = "#0F172A"
            hfg  = "#93C5FD"
        else:
            bg   = "#FFFFFF"
            fg   = "#1E293B"
            sel  = "#DBEAFE"
            hdr  = "#1E40AF"
            hfg  = "#FFFFFF"

        style.configure(
            "Treeview",
            background=bg,
            foreground=fg,
            fieldbackground=bg,
            rowheight=26,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=hdr,
            foreground=hfg,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", sel)],
            foreground=[("selected", fg)],
        )
