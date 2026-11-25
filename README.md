# Precious Metals Tracker

A small desktop app that shows live spot prices for **gold, silver, platinum, and palladium** in a clean window with dark and light themes. No account, no API key, nothing to install beyond Python.

![Dark theme](screenshots/dark.png)
![Light theme](screenshots/light.png)

## Features

- Live prices for gold (Au), silver (Ag), platinum (Pt), and palladium (Pd), in USD per troy ounce
- Auto-refresh every 1 minute, 5 minutes, 30 minutes, or 1 hour
- Dark and light themes, switchable on the fly
- Stays responsive while fetching prices (the network work runs in the background)
- One file, no third-party packages

## Requirements

- Python 3 (with Tkinter, which comes with Python on most systems)
- An internet connection

Developed and tested on Linux Mint.

## Running it

1. Download `metals.py`
2. Open a terminal in the folder where you saved it
3. Run:

```
python3 metals.py
```

If you get an error about `tkinter` on Debian, Ubuntu, or Mint, install it with:

```
sudo apt install python3-tk
```

## How it works

The app asks [gold-api.com](https://gold-api.com) for each metal's price, using a free public endpoint that needs no key. Fetching happens in a background thread and hands its results to the window through a queue, so the window never freezes while it waits on the internet. Each refresh pauses briefly between requests to stay friendly to the free service.

Colors, fonts, metals, and refresh options sit in clearly labeled blocks at the top of `metals.py`, so they're easy to change.

## Data source and disclaimer

Prices come from [gold-api.com](https://gold-api.com) and are used under its [terms of service](https://gold-api.com/terms).

Prices may be delayed or inaccurate. **This is not financial advice. Don't make financial decisions based on this app.**

## Built with

Designed and directed by **HoboChocolate**, built with help from [Claude](https://claude.ai) (Anthropic). Every feature started as a plain-English request, then was read, tested, and tweaked by hand.

## Ideas for later

- Remember the chosen theme and refresh interval between runs
- Show price change since the last refresh
- Choose a different currency
- Price per gram or kilo, as well as per ounce

## License

MIT. See the `LICENSE` file for details.
