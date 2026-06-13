from render import render


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


def test_render_shows_collection_name_and_id():
    html = render(two_records(), count=2, time="x")
    assert "Alpha" in html
    assert "MMS ID# 123" in html


def test_render_shows_all_cuny_when_groups_falsy():
    record = [["Beta", False, False, False, "456", "Collection ID", False]]
    html = render(record, count=1, time="x")
    assert "All CUNY Institutions" in html


def test_render_joins_group_names_when_present():
    record = [
        [
            "A",
            ["Hunter College", "Queens College"],
            False,
            False,
            "1",
            "Collection ID",
            False,
        ]
    ]
    html = render(record, count=1, time="x")
    assert "Hunter College" in html
    assert "Queens College" in html


def test_render_shows_override_none_when_falsy():
    record = [["Beta", False, False, False, "456", "Collection ID", False]]
    html = render(record, count=1, time="x")
    assert "Public name override:" in html
    assert "<em>none</em>" in html


def test_render_shows_override_value_when_present():
    record = [["A", False, False, False, "1", "Collection ID", "Custom Name"]]
    html = render(record, count=1, time="x")
    assert "Public name override: Custom Name" in html
