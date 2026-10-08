# The Dow, 1896–2026

An interactive, log-scale chart of the Dow Jones Industrial Average from 1896 to 2026. It shows 131 headline events, one per year, each with a short summary, archive images from Wikimedia Commons, and the Dow's year-end close and change for that year. A presidents strip runs under the chart, and hovering a president opens a short profile with a portrait. A Compare row adds the S&P 500, Nasdaq, a "Mag 7" basket, Nikkei 225, FTSE 100 and DAX, and a Scale switch toggles between price and "rebased to 100" at the start of the view.

Part of the **Chronographs** series — time-spine history sites that open a long line into stories.

It is a single static page with no build step. It works on GitHub Pages or any static host.

## Run locally

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

Opening `index.html` straight from disk also works in most browsers.

## Publish on GitHub Pages

1. Push this folder to a repository, with `index.html` at the root.
2. In **Settings → Pages**, pick the default branch and the `/ (root)` folder.

## What's in here

| Path | What it is |
|---|---|
| `index.html` | The whole site: markup, styles, script, and the event, price and image data embedded inline |
| `img/` | 294 archive images (JPEG, max 1100 px), named `NNN-K.jpg` by event number |
| `pres/` | 24 presidential portraits and `credits.json` (Trump appears twice, for each term) |
| `data/events.json` | The 131 events: number, year, caption from the original chart, category, summary |
| `data/series.json` | The original approximate monthly Dow line (1896–2016) and year-end closes; the live page now uses the actual monthly Dow in `data/indices.json` |
| `data/indices.json` | Monthly closes as `[t, value]` (t = year + (month − 0.5)/12) for DJI, SPX, IXIC, MAG7, N225, FTSE, DAX |
| `data/indices-raw.json` | The same data as fetched, keyed by `YYYY-MM`, with each Mag 7 ticker and a `meta` block naming the source of every series |
| `data/artefacts.json` | The archive image list for each event, with titles, authors, licenses and Commons links |
| `CREDITS.md` | Attribution for every archive image |
| `tools/` | The scripts used to build the data (see below) |

External dependencies: D3 7.9.0 from cdnjs and three Google Fonts (Bodoni Moda, Libre Franklin, IBM Plex Mono).

## How the data was made

- **Events and captions** were transcribed from the chart "The Dow Jones Industrial Average: 1896–2016" by VirtueofSelfishInvesting.com. Event *n* is always the year 1895 + *n*.
- **Summaries** were written in advance by Claude (Anthropic). They have been spot-checked but not fact-checked line by line.
- **Events 122–131 (2017–2026)** continue the chart in the same one-event-per-year style. They were written by Claude and checked against news reports; 2026 covers the year to date (early October 2026).
- **Prices** are monthly closes. The Dow comes from MeasuringWorth's daily series through 1991 (values before 1915 are scaled to the year-end closes) and from Yahoo Finance from 1992; the other indices come from Yahoo Finance. The Mag 7 line is an equal-weighted, never-rebalanced basket of the seven stocks' dividend-adjusted prices, starting at 100 in December 2015. The latest month is month to date. The earlier approximate series (`tools/build_series.py`, Shiller-shaped) is kept for reference.
- **Archive images** were chosen per event through its category lens, from markets and money to war, politics, innovation, disaster and society. They were fetched from Wikimedia Commons with `tools/fetch_artefacts.py` and `tools/artefacts_plan.json`, and only public-domain or Creative Commons files were kept. Images that were off-topic were then removed by hand.
- `tools/dow-timeline-v9.html` is the current page source before data is embedded, and `tools/build_v9.py` embeds events, images and index data into it. `tools/template.html` is the earlier source.

## Licensing

- The images keep their own licenses, listed in `CREDITS.md` and `pres/credits.json`. Creative Commons BY and BY-SA images need the attribution kept wherever they are reused.
- The event captions come from a third-party chart. Credit VirtueofSelfishInvesting.com when you publish.
- Choose a license for the code and text before publishing; none is set here.
