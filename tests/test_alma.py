import fetch

# --- sub_fetch_groups ---------------------------------------------------------


def test_groups_returns_descriptions():
    sub_json = {
        "group_setting": [
            {"group": {"desc": "Group A"}},
            {"group": {"desc": "Group B"}},
        ]
    }
    assert fetch.sub_fetch_groups(sub_json) == ["Group A", "Group B"]


def test_groups_missing_returns_false():
    assert fetch.sub_fetch_groups({}) is False


# --- sub_fetch_interface ------------------------------------------------------


def test_interface_returns_name():
    assert (
        fetch.sub_fetch_interface({"interface": {"name": "EBSCOhost"}}) == "EBSCOhost"
    )


def test_interface_missing_returns_false():
    assert fetch.sub_fetch_interface({}) is False


# --- sub_fetch_vendors --------------------------------------------------------


def test_vendors_returns_value():
    sub_json = {"interface": {"vendor": {"value": "EBSCO"}}}
    assert fetch.sub_fetch_vendors(sub_json) == "EBSCO"


def test_vendors_missing_returns_false():
    assert fetch.sub_fetch_vendors({"interface": {"name": "x"}}) is False


# --- sub_fetch_public_name_override -------------------------------------------


def test_public_name_override_returns_value():
    assert (
        fetch.sub_fetch_public_name_override({"public_name_override": "Foo"}) == "Foo"
    )


# --- Alma URLs ------------------------------------------------------------------
# Tests that make HTTP calls use the `alma` fixture from conftest.py: a fake
# Alma API that answers only the exact URLs below. The API keys in them are
# the test keys the fixture sets.

ALMA = "https://api-na.hosted.exlibrisgroup.com/almaws/v1"
PAGE_1 = (
    f"{ALMA}/electronic/e-collections?limit=100&offset=0&format=json"
    "&apikey=test-nz-key"
)
PAGE_2 = (
    f"{ALMA}/electronic/e-collections?limit=100&offset=100&format=json"
    "&apikey=test-nz-key"
)
COLLECTION_6101 = f"{ALMA}/electronic/e-collections/6101?apikey=test-nz-key&format=json"
COLLECTION_6102 = f"{ALMA}/electronic/e-collections/6102?apikey=test-nz-key&format=json"
BIB_9901 = f"{ALMA}/bibs/9901?apikey=test-bibs-key&format=json"


# --- sub_fetch_cz_ids (asks Alma for the collection's bib record) -------------


def test_cz_ids_returns_mms_id_from_the_exlcz_network_number(alma):
    alma[BIB_9901] = {"network_number": ["(CKB)5280000000123", "(EXLCZ)5500000012345"]}
    sub_json = {"id": "6101", "resource_metadata": {"mms_id": {"value": "9901"}}}
    assert fetch.sub_fetch_cz_ids(sub_json) == ["5500000012345", "MMS ID"]


def test_cz_ids_falls_back_to_collection_id_when_no_exlcz(alma):
    alma[BIB_9901] = {"network_number": ["(CKB)5280000000123"]}
    sub_json = {"id": "6101", "resource_metadata": {"mms_id": {"value": "9901"}}}
    assert fetch.sub_fetch_cz_ids(sub_json) == ["6101", "Collection ID"]


def test_cz_ids_falls_back_to_collection_id_when_no_resource_metadata(alma):
    assert fetch.sub_fetch_cz_ids({"id": "6101"}) == ["6101", "Collection ID"]


# --- fetch_records (the whole Alma fetch) ---------------------------------------


def test_fetch_records_returns_every_field_of_a_collection(alma):
    alma[PAGE_1] = {
        "total_record_count": 1,
        "electronic_collection": [
            {"id": "6101", "public_name": "Academic Search Complete"}
        ],
    }
    alma[COLLECTION_6101] = {
        "id": "6101",
        "public_name": "Academic Search Complete",
        "public_name_override": "ASC",
        "interface": {"name": "EBSCOhost", "vendor": {"value": "EBSCO"}},
        "group_setting": [{"group": {"value": "HC", "desc": "Hunter College"}}],
        "resource_metadata": {"mms_id": {"value": "9901"}},
    }
    alma[BIB_9901] = {"network_number": ["(EXLCZ)5500000012345"]}
    assert fetch.fetch_records() == [
        (
            "Academic Search Complete",
            ["Hunter College"],
            "EBSCOhost",
            "EBSCO",
            "5500000012345",
            "MMS ID",
            "ASC",
        )
    ]


def test_fetch_records_requests_every_page(alma):
    # 101 collections need two pages of 100. Each fake page holds just one
    # collection to keep the test short.
    alma[PAGE_1] = {
        "total_record_count": 101,
        "electronic_collection": [{"id": "6101", "public_name": "On Page One"}],
    }
    alma[PAGE_2] = {
        "total_record_count": 101,
        "electronic_collection": [{"id": "6102", "public_name": "On Page Two"}],
    }
    alma[COLLECTION_6101] = {"id": "6101", "public_name_override": ""}
    alma[COLLECTION_6102] = {"id": "6102", "public_name_override": ""}
    assert fetch.fetch_records() == [
        ("On Page One", False, False, False, "6101", "Collection ID", ""),
        ("On Page Two", False, False, False, "6102", "Collection ID", ""),
    ]


def test_fetch_records_requests_no_extra_page_for_exactly_100(alma):
    # 100 collections fit on one page. A request for PAGE_2 would fail the
    # test, because the fake doesn't know that URL.
    alma[PAGE_1] = {
        "total_record_count": 100,
        "electronic_collection": [{"id": "6101", "public_name": "Only Page"}],
    }
    alma[COLLECTION_6101] = {"id": "6101", "public_name_override": ""}
    assert fetch.fetch_records() == [
        ("Only Page", False, False, False, "6101", "Collection ID", "")
    ]
