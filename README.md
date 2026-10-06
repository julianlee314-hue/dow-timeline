# The Dow, 1896–2016

An interactive, log-scale chart of the Dow Jones Industrial Average from 1896 to 2016. It shows 121 headline events, one per year, each with a short summary, archive images from Wikimedia Commons, and the Dow's year-end close and change for that year. A presidents strip runs under the chart, and hovering a president opens a short profile with a portrait.

It is a single static page with no build step. It works on GitHub Pages or any static host.

**Live versions**

| Version | Path | URL |
|---|---|---|
| **v0.1** (current root) | `/` | [julianlee314-hue.github.io/dow-timeline/](https://julianlee314-hue.github.io/dow-timeline/) |
| **v0.2** | `/v0.2/` | [julianlee314-hue.github.io/dow-timeline/v0.2/](https://julianlee314-hue.github.io/dow-timeline/v0.2/) |

The original build stays at the site root. The newer build lives under `v0.2/`.

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
| `img/` | 268 archive images (JPEG, max 1000 px), named `NNN-K.jpg` by event number |
| `pres/` | 21 presidential portraits (240×300) and `credits.json` |
| `data/events.json` | The 121 events: number, year, caption from the original chart, category, summary |
| `data/series.json` | Approximate monthly Dow values and the year-end closes |
| `data/artefacts.json` | The archive image list for each event, with titles, authors, licenses and Commons links |
| `CREDITS.md` | Attribution for every archive image |
| `tools/` | The scripts used to build the data (see below) |
| `v0.2/` | Newer site build (same layout), served at `/v0.2/` |

External dependencies: D3 7.9.0 from cdnjs and three Google Fonts (Bodoni Moda, Libre Franklin, IBM Plex Mono).

## How the data was made

- **Events and captions** were transcribed from the chart "The Dow Jones Industrial Average: 1896–2016" by VirtueofSelfishInvesting.com. Event *n* is always the year 1895 + *n*.
- **Summaries** were written in advance by Claude (Anthropic). They have been spot-checked but not fact-checked line by line.
- **Prices are approximate.** Year-end closes come from the public DJIA record. The monthly line between them follows the shape of Robert Shiller's monthly S&P index, scaled to match each Dow year-end (`tools/build_series.py`).
- **Archive images** were chosen per event through its category lens, from markets and money to war, politics, innovation, disaster and society. They were fetched from Wikimedia Commons with `tools/fetch_artefacts.py` and `tools/artefacts_plan.json`, and only public-domain or Creative Commons files were kept. Images that were off-topic were then removed by hand.
- `tools/template.html` is the page source before the data is embedded.

## Licensing

- The images keep their own licenses, listed in `CREDITS.md` and `pres/credits.json`. Creative Commons BY and BY-SA images need the attribution kept wherever they are reused.
- The event captions come from a third-party chart. Credit VirtueofSelfishInvesting.com when you publish.
- Choose a license for the code and text before publishing; none is set here.
