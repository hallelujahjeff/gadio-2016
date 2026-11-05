GADIO 2016 — local preview

Start (Python 3.10+, no dependencies):
  python server.py --direct
Open http://127.0.0.1:2016

Omit --direct if your network requires the configured environment proxy.
The server binds only to this computer. Ctrl+C stops it.

public/ contains the static frontend. server.py serves it and exposes the
same-origin /api/radios proxy. No account, database, or historical catalog.
The proxy computes today minus ten calendar years in UTC+8, clamps leap days,
and includes the whole historical day. Responses are cached for ten minutes.
The UI uses 21 records per page; one extra upstream record detects next page.
Current category assignments and metadata come from Gcores, not 2016 snapshots.
The top panels use original 2016 background and logo assets recovered from
Wayback Machine. Episode images are live.

Verify upstream date/order/pagination semantics:
  python verify_gcores.py --date 2016-11-04 --direct

This is an unofficial local recreation. Content and images belong to their
respective owners. No audio is hosted; episode links open the official site.

Cloudflare Workers deployment (Free plan; no database or storage product):
  npm ci
  npm test
  npm run check
  npx wrangler login
  npm run deploy

Keep the Cloudflare account on Workers Free. This configuration does not
subscribe to a paid plan or create D1, R2, KV, or image transformation services.
Wrangler prints the workers.dev URL after deployment. The account must already
be registered; complete any account agreement yourself in Cloudflare.

Worker local preview:
  npm run dev
  http://127.0.0.1:2017

worker/index.js is the production proxy; public/ is uploaded as static assets.
Only /api/* and /image/* run Worker-first; ordinary files use static serving.
API cache entries include the UTC+8 date and expire after ten minutes; image
cache entries expire after one day. Cache hits still invoke the Worker and
count toward its request quota. No historical episode catalog is persisted.
Authentication belongs to the official Wrangler login flow. Never put API
tokens in source code, chat messages, wrangler.jsonc, or the public/ directory.

GitHub Pages (static build, no Cloudflare dependency):
  python scripts/build_pages.py --direct
  python -m http.server 2018 --bind 127.0.0.1 --directory dist

The builder downloads current Gcores program metadata and covers, then writes
dist/. It includes fourteen days of future replay data; the browser hides all
programs after today's UTC+8 date minus ten calendar years. Category selection
and pagination happen locally. All asset paths support a repository subpath.

Upload public/, scripts/, and .github/workflows/pages.yml to the main branch
of a public repository. In Settings > Pages select GitHub Actions as Source.
The workflow builds and deploys on push, manual dispatch, and daily at 00:17
UTC+8. Schedules can be delayed; public-repository scheduled workflows may be
disabled after 60 days without repository activity. Re-enable in Actions if
GitHub disables it. No credentials are needed to read public Gcores data.
The dist/ output and downloaded covers are deployment artifacts, not source.
