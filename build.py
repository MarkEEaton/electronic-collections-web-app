"""Build the static site: fetch from Alma, render HTML, write ``dist/``.

This is the single entry point run by the GitHub Action (and locally with a
``.env`` holding the API keys). It replaces the old Flask app + cron split.
"""

import os
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo

from fetch import fetch_records
from transform import normalize_records
from render import render

DIST = "dist"
STATIC = "static"
ASSETS = ("main.css", "bootstrap.min.css")
CUSTOM_DOMAIN = "electroniccollections.ocert.at"


def build():
    records = normalize_records(fetch_records())
    now = datetime.now(ZoneInfo("America/New_York"))
    time = now.strftime("%-I:%M%p (%Z)")
    html = render(records, count=len(records), time=time)

    os.makedirs(DIST, exist_ok=True)
    for name in ASSETS:
        shutil.copyfile(os.path.join(STATIC, name), os.path.join(DIST, name))
    with open(os.path.join(DIST, "index.html"), "w") as f:
        f.write(html)
    # Preserve the custom domain across artifact-based Pages deploys.
    with open(os.path.join(DIST, "CNAME"), "w") as f:
        f.write(CUSTOM_DOMAIN + "\n")


if __name__ == "__main__":
    build()
