import re

from render import render


def table_text(html):
    """The table's text as a reader sees it: tags removed, whitespace collapsed."""
    tbody = html.split("<tbody>")[1].split("</tbody>")[0]
    return " ".join(re.sub(r"<[^>]+>", " ", tbody).split())


def two_records():
    return [
        [
            "Alpha",
            ["Hunter College"],
            "EBSCOhost",
            "EBSCO",
            "123",
            "MMS ID",
            "Alt Name",
        ],
        ["Beta", False, False, False, "456", "Collection ID", False],
    ]


def test_render_includes_count_and_time():
    html = render(two_records(), count=2, time="3:00PM (EST)")
    assert "2 electronic collections" in html
    assert "3:00PM (EST)" in html


def test_render_emits_one_row_per_record():
    html = render(two_records(), count=2, time="x")
    assert html.count('scope="row"') == 2


def test_render_shows_every_field_of_a_full_record():
    record = [
        "Alpha",
        ["Hunter College", "Queens College"],
        "EBSCOhost",
        "EBSCO",
        "123",
        "MMS ID",
        "Alt Name",
    ]
    html = render([record], count=1, time="x")
    assert table_text(html) == (
        "Alpha (MMS ID# 123) "
        "Public name override: Alt Name "
        "Groups: Hunter College, Queens College "
        "Interface name: EBSCOhost "
        "Vendor name: EBSCO"
    )


def test_render_shows_defaults_when_optional_fields_are_missing():
    # False groups means the collection is available to every CUNY school.
    record = ["Beta", False, False, False, "456", "Collection ID", False]
    html = render([record], count=1, time="x")
    assert table_text(html) == (
        "Beta (Collection ID# 456) "
        "Public name override: none "
        "Groups: All CUNY Institutions"
    )


def test_render_escapes_html_in_collection_names():
    # Unescaped, the "<" would start a tag and break the page.
    record = ["Taylor & Francis <Archive>", False, False, False, "1", "x", False]
    html = render([record], count=1, time="x")
    assert "Taylor &amp; Francis &lt;Archive&gt;" in html
