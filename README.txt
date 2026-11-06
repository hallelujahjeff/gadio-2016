GADIO 2016 — GitHub Pages

Build: python scripts/build_pages.py
Preview: python -m http.server 2018 --bind 127.0.0.1 --directory dist

The site reads data/radios-all.json and filters publishedTimestamp in the
browser. The cutoff is the end of today minus ten calendar years in UTC+8.
Leap days are clamped. Pagination and category filters run locally.
No daily build or live metadata API is required. The committed snapshot has
8,245 public programs as of 2026-11-05. Deleted/private records are excluded.
Covers use bundled files where available, otherwise their original CDN URLs.

Refresh the full snapshot occasionally with:
  python scripts/export_radios.py --direct
Commit the refreshed JSON to main. Pages builds on push or manual dispatch.
The export script downloads metadata only, not images or audio.

Original 2016 category artwork is recovered from Wayback Machine.
This is an unofficial recreation. Content belongs to its original owners.
Episode links open the official Gcores playback page.

Visitor count (GoatCounter):
The site sends page views to https://gadio2016.goatcounter.com/ and shows
the total in a small footer label. The GoatCounter setting "Allow adding
visitor counts on your website" is enabled. Build and deploy to publish
the integration. The official ISC-licensed count.js is bundled locally
because its CDN may be unreachable from some networks; collection still
requires access to the GoatCounter subdomain. The public count can be
cached for up to four hours.
