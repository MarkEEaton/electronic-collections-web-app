# electronic-collections-web-app

For the Alma Extensibility Task Force.

This project lists the activated Network Zone electronic collections at CUNY,
queried from the Alma API, and displays them as a web page shared on the OLS
LibAnswers Knowledge Base (embedded as an iframe).

## Architecture

It is a **static site on GitHub Pages**, rebuilt hourly by a **GitHub Action**.
There is no server to run or pay for.

```
GitHub Action (hourly cron)
  fetch.py      -> calls the Alma API, returns records
  transform.py  -> swaps outdated library names, sorts
  render.py     -> renders templates/index.html (Jinja) to HTML
  build.py      -> writes dist/ (index.html + CSS + CNAME)
        |
        v
  upload-pages-artifact -> deploy-pages -> GitHub Pages
        |
        v
  https://electroniccollections.ocert.at  (embedded in LibAnswers)
```

The page is plain HTML with no client-side JavaScript.

## Local development

Requires [uv](https://docs.astral.sh/uv/). Put the two Alma API keys in a
local `.env` (never commit it):

```
NZ_API_KEY=...
BIBS_NZ_API_KEY=...
```

```bash
uv sync                    # install dependencies
uv run pytest              # run the test suite
uv run python build.py     # build dist/ ; open dist/index.html in a browser
```

`build.py` performs live Alma API calls, so it needs the keys. The tests do not
touch the network (the one HTTP-calling function is monkeypatched).

## Deployment (one-time GitHub setup)

These steps are done in the GitHub UI / DNS and cannot be scripted here:

1. **Settings → Pages → Source** = "GitHub Actions".
2. **Settings → Secrets and variables → Actions** — add repository secrets
   `NZ_API_KEY` and `BIBS_NZ_API_KEY`.
3. Trigger the workflow manually (**Actions → Build and deploy → Run workflow**)
   and confirm the deploy succeeds on the default
   `https://<org>.github.io/electronic-collections-web-app/` URL.
4. **Repoint DNS:** point `electroniccollections.ocert.at` (a `CNAME` record) at
   `markeeaton.github.io`, replacing the old PythonAnywhere target.
5. **Settings → Pages → Custom domain** = `electroniccollections.ocert.at`; once
   the certificate provisions, enable **Enforce HTTPS**.

Because the public URL is unchanged, **the LibAnswers iframe needs no edits**.

### Note on security headers

GitHub Pages cannot send HTTP response headers, so the previous
`Content-Security-Policy: frame-ancestors ...` restriction (which limited iframe
embedding to LibAnswers) is no longer enforced. The rest of the CSP is applied
via a `<meta>` tag in the page. This is acceptable for public, read-only data.
