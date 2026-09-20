"""
Shared visual theme: dark "SOC dashboard" look, matching the app logo's
lime-on-black palette. Every window calls apply_theme(root) once and then
uses the COLORS / FONTS constants below for anything custom (Canvas,
Listbox, Label backgrounds, etc. -- ttk widgets pick up the theme
automatically via the style names registered here).
"""
from __future__ import annotations  # lets "X | Y" type hints work on Python 3.9

import os
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import config

COLORS = {
    "bg": "#0b0e14",          # near-black app background
    "panel": "#121826",       # card / panel background
    "panel_alt": "#161f2e",   # slightly lighter panel (headers, stripes)
    "border": "#232f42",
    "accent": "#c7d92e",      # lime-green from the logo crown
    "accent_dark": "#9aab1f",
    "text": "#e6edf3",
    "text_dim": "#8b96a8",
    "danger": "#ff5c5c",
    "success": "#3fd67a",
    "warning": "#ffb648",
}

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUBTITLE = ("Segoe UI", 11)
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 9)
FONT_BUTTON = ("Segoe UI", 10, "bold")

_image_cache = []  # keep references alive so Tk doesn't garbage-collect them


def apply_theme(root: tk.Tk | tk.Toplevel) -> ttk.Style:
    """Call once per top-level window. Sets background + a dark ttk style."""
    root.configure(bg=COLORS["bg"])
    set_window_icon(root)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Panel.TFrame", background=COLORS["panel"], relief="flat")
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=FONT_NORMAL)
    style.configure("Panel.TLabel", background=COLORS["panel"], foreground=COLORS["text"], font=FONT_NORMAL)
    style.configure("Dim.TLabel", background=COLORS["panel"], foreground=COLORS["text_dim"], font=FONT_NORMAL)
    style.configure("Heading.TLabel", background=COLORS["panel"], foreground=COLORS["text"], font=FONT_HEADING)
    style.configure("Stat.TLabel", background=COLORS["panel"], foreground=COLORS["accent"], font=("Segoe UI", 18, "bold"))
    style.configure("Title.TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=FONT_TITLE)

    style.configure(
        "Accent.TButton",
        background=COLORS["accent"], foreground="#0b0e14",
        font=FONT_BUTTON, borderwidth=0, focuscolor=COLORS["accent"], padding=(14, 8),
    )
    style.map("Accent.TButton",
              background=[("active", COLORS["accent_dark"]), ("disabled", COLORS["border"])],
              foreground=[("disabled", COLORS["text_dim"])])

    style.configure(
        "Dark.TButton",
        background=COLORS["panel_alt"], foreground=COLORS["text"],
        font=FONT_BUTTON, borderwidth=1, focuscolor=COLORS["panel_alt"], padding=(12, 7),
    )
    style.map("Dark.TButton",
              background=[("active", COLORS["border"])],
              bordercolor=[("!disabled", COLORS["border"])])

    style.configure(
        "Danger.TButton",
        background=COLORS["danger"], foreground="#1a0000",
        font=FONT_BUTTON, borderwidth=0, padding=(12, 7),
    )
    style.map("Danger.TButton", background=[("active", "#cc3f3f")])

    style.configure("TEntry", fieldbackground=COLORS["panel_alt"], foreground=COLORS["text"],
                     insertcolor=COLORS["text"], bordercolor=COLORS["border"], padding=6)
    style.configure("TCombobox", fieldbackground=COLORS["panel_alt"], background=COLORS["panel_alt"],
                     foreground=COLORS["text"], arrowcolor=COLORS["accent"])
    style.map("TCombobox", fieldbackground=[("readonly", COLORS["panel_alt"])],
              foreground=[("readonly", COLORS["text"])])

    style.configure("Treeview", background=COLORS["panel_alt"], fieldbackground=COLORS["panel_alt"],
                     foreground=COLORS["text"], rowheight=26, borderwidth=0, font=FONT_NORMAL)
    style.configure("Treeview.Heading", background=COLORS["panel"], foreground=COLORS["accent"],
                     font=FONT_HEADING, relief="flat")
    style.map("Treeview", background=[("selected", COLORS["accent_dark"])],
              foreground=[("selected", "#0b0e14")])

    style.configure("TCheckbutton", background=COLORS["bg"], foreground=COLORS["text"], font=FONT_NORMAL)
    style.configure("TLabelframe", background=COLORS["panel"], bordercolor=COLORS["border"])
    style.configure("TLabelframe.Label", background=COLORS["panel"], foreground=COLORS["accent"], font=FONT_HEADING)

    return style


def set_window_icon(window) -> None:
    icon_path = os.path.join(config.BASE_DIR, "assets", "icon.ico")
    png_path = os.path.join(config.BASE_DIR, "assets", "logo.png")
    try:
        window.iconbitmap(icon_path)  # works on Windows
    except tk.TclError:
        try:
            img = tk.PhotoImage(file=png_path)
            _image_cache.append(img)
            window.iconphoto(True, img)  # cross-platform fallback (Linux/macOS)
        except tk.TclError:
            pass


def load_logo(size: int = 72) -> ImageTk.PhotoImage:
    """Returns a Tk-compatible image of the app logo resized to `size` px square."""
    png_path = os.path.join(config.BASE_DIR, "assets", "logo.png")
    img = Image.open(png_path).convert("RGBA").resize((size, size), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    _image_cache.append(photo)  # prevent garbage collection
    return photo
