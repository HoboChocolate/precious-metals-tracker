import json
import queue
import threading
import time
import tkinter as tk
from urllib.request import Request, urlopen


# Precious Metals Tracker. Designed by HoboChocolate 
# Built with help from Claude.
# Wanted a simple and free Precious Metals Tracker for my desktop.
# Couldn't find one, so here it is.
# Functionality and simplicity now. Bells and whistles later on.

# AU is that Gold?!
# Ag it's just Silver.'

# -----     -----

# Make it Pretty

# ---- Themes ----
THEMES = {
    "Dark": {
        "bg": "#1e1e1e",          # window background
        "card": "#2a2a2a",        # background of each metal row
        "text": "#e0e0e0",        # default text
        "muted": "#8a8a8a",       # small, quiet text
        "menu_bg": "#2d2d2d",     # dropdown background
        "menu_hover": "#3a3a3a",  # dropdown when hovered
        "metals": {
            "XAU": "#ffd700",     # gold yellow
            "XAG": "#c8c8c8",     # light grey
            "XPT": "#7fd4f0",     # icy blue
            "XPD": "#c9a0e8",     # soft violet
        },
    },
    "Light": {
        "bg": "#f2f2f2",
        "card": "#ffffff",
        "text": "#222222",
        "muted": "#666666",
        "menu_bg": "#e4e4e4",
        "menu_hover": "#d4d4d4",
        "metals": {
            "XAU": "#b8860b",     # deep gold
            "XAG": "#6b6b6b",     # medium grey
            "XPT": "#1f7fa8",     # steel blue
            "XPD": "#7b4fa6",     # purple
        },
    },
}

# ---- Fonts (name, size, style) ----
FONT_TITLE = ("Arial", 16, "bold")
FONT_SUBTITLE = ("Arial", 10)
FONT_NAME = ("Arial", 14, "bold")
FONT_PRICE = ("Arial", 20, "bold")
FONT_SMALL = ("Arial", 10)
FONT_MENU = ("Arial", 13)     # dropdown menus

# display name, symbol used to ask for the price
METALS = [
    ("Au  Gold", "XAU"),
    ("Ag  Silver", "XAG"),
    ("Pt  Platinum", "XPT"),
    ("Pd  Palladium", "XPD"),
]

# Dropdown choices: label -> seconds
INTERVALS = {
    "1 minute": 60,
    "5 minutes": 300,
    "30 minutes": 1800,
    "1 hour": 3600,
}

result_queue = queue.Queue()  # the "mailbox" the worker drops results into
refresh_id = None             # remembers the pending timer so we can cancel it
is_fetching = False           # True while the worker is busy


# Do Some Work


def get_price(symbol):
    """Ask gold-api.com for one metal's price in USD."""
    url = f"https://api.gold-api.com/price/{symbol}"
    request = Request(url, headers={"User-Agent": "metals-tracker"})
    with urlopen(request, timeout=10) as response:
        return json.load(response)["price"]


def fetch_all():
    """WORKER: runs in the background. Never touches the window."""
    results = {}
    for name, symbol in METALS:
        try:
            results[symbol] = f"${get_price(symbol):,.2f}"
        except Exception:
            results[symbol] = "unavailable"
        time.sleep(0.5)  # be polite: no more than ~2 requests per second
    result_queue.put(results)


def refresh():
    """Start a background fetch, then begin watching the mailbox."""
    global is_fetching
    if is_fetching:
        return
    is_fetching = True
    status.config(text="Updating...")
    threading.Thread(target=fetch_all, daemon=True).start()
    window.after(100, check_results)


def check_results():
    """Check the mailbox. If results arrived, show them and schedule the next refresh."""
    global is_fetching, refresh_id
    try:
        results = result_queue.get_nowait()
    except queue.Empty:
        window.after(100, check_results)
        return

    for symbol, text in results.items():
        metal_widgets[symbol]["price"].config(text=text)
    status.config(text="Last updated: " + time.strftime("%I:%M:%S %p %Z"))

    is_fetching = False
    seconds = INTERVALS[interval_choice.get()]
    refresh_id = window.after(seconds * 1000, refresh)


def on_interval_change(*args):
    """When the refresh dropdown changes, cancel the old timer and refresh now."""
    if refresh_id is not None:
        window.after_cancel(refresh_id)
    refresh()


def apply_theme(*args):
    """Recolor every widget using the currently chosen theme."""
    t = THEMES[theme_choice.get()]

    window.configure(bg=t["bg"])
    for frame in (footer, settings):
        frame.configure(bg=t["bg"])

    title.configure(bg=t["bg"], fg=t["text"])
    subtitle.configure(bg=t["bg"], fg=t["muted"])
    status.configure(bg=t["bg"], fg=t["muted"])
    for label in (refresh_label, theme_label):
        label.configure(bg=t["bg"], fg=t["text"])

    for symbol, parts in metal_widgets.items():
        color = t["metals"][symbol]
        parts["card"].configure(bg=t["card"])
        parts["stripe"].configure(bg=color)
        parts["name"].configure(bg=t["card"], fg=color)
        parts["price"].configure(bg=t["card"], fg=color)

    for dropdown in (interval_dropdown, theme_dropdown):
        dropdown.configure(
            bg=t["menu_bg"], fg=t["text"],
            activebackground=t["menu_hover"], activeforeground=t["text"],
        )
        dropdown["menu"].configure(
            bg=t["menu_bg"], fg=t["text"],
            activebackground=t["menu_hover"], activeforeground=t["text"],
        )

# Meat and Potatoes

# ---- Build the window ----
window = tk.Tk()
window.title("Precious Metals Prices")
window.geometry("500x500")
window.minsize(480, 480)

theme_choice = tk.StringVar(value="Dark")
interval_choice = tk.StringVar(value="1 minute")

# Header
title = tk.Label(window, text="Precious Metals", font=FONT_TITLE)
title.pack(pady=(20, 0))

subtitle = tk.Label(
    window, text="Live spot prices, USD per troy ounce", font=FONT_SUBTITLE
)
subtitle.pack(pady=(2, 14))

# One "card" per metal. We remember each piece so apply_theme() can recolor it.
metal_widgets = {}
for name, symbol in METALS:
    card = tk.Frame(window)
    card.pack(fill="x", padx=20, pady=5)

    stripe = tk.Frame(card, width=6)
    stripe.pack(side="left", fill="y")

    name_label = tk.Label(card, text=name, font=FONT_NAME, anchor="w")
    name_label.pack(side="left", padx=14, pady=12)

    price_label = tk.Label(card, text="loading...", font=FONT_PRICE, anchor="e")
    price_label.pack(side="right", padx=14, pady=12)

    metal_widgets[symbol] = {
        "card": card, "stripe": stripe, "name": name_label, "price": price_label,
    }



# Settings row: refresh dropdown and theme dropdown
settings = tk.Frame(window)
settings.pack(fill="x", padx=20, pady=(4, 12))

refresh_label = tk.Label(settings, text="Refresh every:", font=FONT_SMALL)
refresh_label.pack(side="left", padx=(0, 6))

interval_dropdown = tk.OptionMenu(settings, interval_choice, *INTERVALS.keys())
interval_dropdown.config(highlightthickness=0, bd=0, font=FONT_MENU)
interval_dropdown["menu"].config(font=FONT_MENU)
interval_dropdown.pack(side="left")

theme_dropdown = tk.OptionMenu(settings, theme_choice, *THEMES.keys())
theme_dropdown.config(highlightthickness=0, bd=0, font=FONT_MENU)
theme_dropdown["menu"].config(font=FONT_MENU)
theme_dropdown.pack(side="right")

theme_label = tk.Label(settings, text="Theme:", font=FONT_SMALL)
theme_label.pack(side="right", padx=(0, 6))

# Footer: last-updated time, centered at the bottom
footer = tk.Frame(window)
footer.pack(fill="x", padx=20, pady=(0, 14))

status = tk.Label(footer, text="", font=FONT_SMALL)
status.pack()

# Hook up the dropdowns, color everything, and start
interval_choice.trace_add("write", on_interval_change)
theme_choice.trace_add("write", apply_theme)
apply_theme()

window.after(100, refresh)  # first fetch, just after the window appears
window.mainloop()

# HoboChocolate (R. Johnson)/Claude 11/24/2026
