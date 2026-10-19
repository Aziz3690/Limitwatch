# LimitWatch v1

Tracks AI coding tool plan prices, credits, and rate limits.

- Data: `data/tools.json`, `data/changes.json` (edit, then rebuild)
- Build: `python3 scripts/build.py` → `dist/` (gitignored; the Pages workflow builds it)
- Preview: `python3 -m http.server 8080 -d dist` → http://localhost:8080
- Watch pricing pages: `python3 scripts/watch.py` (`snapshots/`; exit 1 and a `.diff` file on change; Replit 403s via plain fetch — check manually)
- Deps: Python 3. Watch also needs beautifulsoup4 (`pip install -r requirements.txt`)

Pages, tool pages, and stylesheets use relative links (`style.css`, `tools/….html`, `../style.css`), so the same `dist/` works at a local server root and at https://aziz3690.github.io/Limitwatch/.

## GitHub Actions

- `.github/workflows/pages.yml` — on push to `main` and on manual dispatch, runs `python3 scripts/build.py` and deploys `dist/` with `actions/configure-pages`, `actions/upload-pages-artifact`, and `actions/deploy-pages`.
- `.github/workflows/watch.yml` — daily (07:00 UTC) and on manual dispatch, runs `python3 scripts/watch.py`, commits updated `snapshots/`, and when the script exits 1 opens an issue titled `Pricing page changed: <date>` with the diff.

### One-time setup

In the repository, open **Settings → Pages → Build and deployment** and set **Source** to **GitHub Actions**. Actions cannot enable Pages with the default workflow token. After that, a push to `main` publishes https://aziz3690.github.io/Limitwatch/.

If a ruleset blocks direct pushes to `main`, allow GitHub Actions to push snapshot commits so the daily watch job can update `snapshots/`.
