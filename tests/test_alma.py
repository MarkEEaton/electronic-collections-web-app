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


# --- sub_fetch_cz_ids (makes a second HTTP call; monkeypatched) ---------------
# pytest's `monkeypatch` fixture (a pytest-advanced technique) swaps out
# httpx.get so the test never hits the network.


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_cz_ids_returns_mms_id_when_exlcz_number_present(monkeypatch):
    sub_json = {
        "id": "9999",
        "resource_metadata": {"mms_id": {"value": "nz-123"}},
    }
    monkeypatch.setattr(
        fetch.httpx,
        "get",
        lambda *a, **k: _FakeResponse({"network_number": ["(EXLCZ)5500000012345"]}),
    )
    assert fetch.sub_fetch_cz_ids(sub_json) == ["5500000012345", "MMS ID"]


def test_cz_ids_falls_back_to_collection_id_when_no_exlcz(monkeypatch):
    sub_json = {
        "id": "9999",
        "resource_metadata": {"mms_id": {"value": "nz-123"}},
    }
    monkeypatch.setattr(
        fetch.httpx,
        "get",
        lambda *a, **k: _FakeResponse({"network_number": ["(SomethingElse)abc"]}),
    )
    assert fetch.sub_fetch_cz_ids(sub_json) == ["9999", "Collection ID"]


def test_cz_ids_falls_back_to_collection_id_when_no_resource_metadata():
    assert fetch.sub_fetch_cz_ids({"id": "9999"}) == ["9999", "Collection ID"]
