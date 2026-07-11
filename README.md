# Airport Diagram Finder

A one-click search box that opens the current FAA airport diagram PDF for
any ICAO or FAA airport identifier, in a new tab.

## Files

- `index.html` — the whole site (HTML, CSS, and JS in one file).
- `airports.json` — lookup table of airport code → current diagram PDF URL.
  Ships with just `KDSM`/`DSM` as a working sample.
- `generate_airports_json.py` — regenerates `airports.json` from the FAA's
  official chart metadata. **Run this locally, not on the web host.**

## How it works

The FAA republishes its airport diagrams every 28 days, and the PDF
filenames change with each cycle. Rather than have every visitor's
browser download the FAA's full ~20,000-chart metadata file on each
search, `generate_airports_json.py` does that once, keeps only the
airport-diagram entries, and writes a small `airports.json`. The website
loads that file once on page load and then every search is instant and
opens the PDF synchronously in a new tab (so it isn't blocked as a pop-up).

## Local testing

Browsers block `fetch()` of local files opened via `file://`, so serve
the folder instead of double-clicking `index.html`:

```
python3 -m http.server 8000
```

Then open http://localhost:8000 and search `KDSM`.

## Updating the data

Every ~28 days, when the FAA publishes a new chart cycle:

```
python3 generate_airports_json.py
```

Then re-upload the new `airports.json` to your web host (`index.html`
never needs to change).

## Deploying

Upload `index.html` and `airports.json` to your web host's document
root. No server-side code, build step, or database is required — it's
a static site.
