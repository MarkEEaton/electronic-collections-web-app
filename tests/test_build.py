import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

import build

PROJECT = Path(__file__).resolve().parent.parent

ALMA = "https://api-na.hosted.exlibrisgroup.com/almaws/v1"
PAGE_1 = (
    f"{ALMA}/electronic/e-collections?limit=100&offset=0&format=json"
    "&apikey=test-nz-key"
)
COLLECTION_6101 = f"{ALMA}/electronic/e-collections/6101?apikey=test-nz-key&format=json"
COLLECTION_6102 = f"{ALMA}/electronic/e-collections/6102?apikey=test-nz-key&format=json"


class FrozenClock(datetime):
    """A datetime whose now() is always 20:05 UTC on 15 January 2026,
    which is 3:05PM Eastern Standard Time in New York."""

    @classmethod
    def now(cls, tz=None):
        return datetime(2026, 1, 15, 20, 5, tzinfo=timezone.utc).astimezone(tz)


@pytest.fixture
def site(alma, monkeypatch, tmp_path):
    """Run build() in an empty folder against the fake Alma API and a
    frozen clock. Returns the dist/ folder it wrote."""
    shutil.copytree(PROJECT / "static", tmp_path / "static")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(build, "datetime", FrozenClock)
    # Alma returns the collections unsorted, and one still uses an old
    # school name.
    alma[PAGE_1] = {
        "total_record_count": 2,
        "electronic_collection": [
            {"id": "6102", "public_name": "Elsevier ScienceDirect"},
            {"id": "6101", "public_name": "eBook Academic Collection"},
        ],
    }
    alma[COLLECTION_6101] = {
        "id": "6101",
        "public_name_override": "",
        "group_setting": [
            {"group": {"value": "MCC", "desc": "Manhattan Community College"}}
        ],
    }
    alma[COLLECTION_6102] = {"id": "6102", "public_name_override": ""}
    build.build()
    return tmp_path / "dist"


def test_build_lists_collections_sorted_with_current_school_names(site):
    html = (site / "index.html").read_text()
    assert html.index("eBook Academic Collection") < html.index(
        "Elsevier ScienceDirect"
    )
    assert "Borough of Manhattan Community College" in html


def test_build_states_count_and_new_york_update_time(site):
    html = (site / "index.html").read_text()
    assert "There are currently 2 electronic collections in the NZ." in html
    assert "The last update was at 3:05PM (EST)." in html


def test_build_writes_cname_for_custom_domain(site):
    assert (site / "CNAME").read_text() == "electroniccollections.ocert.at\n"


def test_build_replaces_the_page_when_run_again(site, alma):
    # Locally, dist/ is still there from the previous build. The `site`
    # fixture already built once; `alma` is the same fake it filled.
    alma[PAGE_1] = {
        "total_record_count": 1,
        "electronic_collection": [
            {"id": "6102", "public_name": "Elsevier ScienceDirect"}
        ],
    }
    build.build()
    html = (site / "index.html").read_text()
    assert "Elsevier ScienceDirect" in html
    assert "eBook Academic Collection" not in html


def test_build_copies_the_stylesheets_the_page_links(site):
    html = (site / "index.html").read_text()
    assert 'href="main.css"' in html
    assert 'href="bootstrap.min.css"' in html
    assert (site / "main.css").read_bytes() == (
        PROJECT / "static" / "main.css"
    ).read_bytes()
    assert (site / "bootstrap.min.css").read_bytes() == (
        PROJECT / "static" / "bootstrap.min.css"
    ).read_bytes()
