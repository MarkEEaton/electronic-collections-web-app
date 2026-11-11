from transform import swap_school_names, normalize_records


def test_swaps_manhattan_community_college_to_bmcc():
    groups = ["Manhattan Community College"]
    assert swap_school_names(groups) == ["Borough of Manhattan Community College"]


def test_swaps_laguardia_library_to_laguardia_community_college():
    groups = ["Fiorello H LaGuardia Community College Library"]
    assert swap_school_names(groups) == ["LaGuardia Community College"]


def test_leaves_other_school_names_untouched():
    groups = ["Hunter College", "Queens College"]
    assert swap_school_names(groups) == ["Hunter College", "Queens College"]


def test_tolerates_false_groups_for_all_institutions():
    assert swap_school_names(False) is False


def test_normalize_sorts_records_case_insensitively_by_public_name():
    # A case-sensitive sort would put "Elsevier" first, because "E" < "e".
    records = [
        ["Elsevier ScienceDirect", False, False, False, "1", "Collection ID", False],
        ["eBook Academic Collection", False, False, False, "2", "Collection ID", False],
    ]
    assert normalize_records(records) == [
        ["eBook Academic Collection", False, False, False, "2", "Collection ID", False],
        ["Elsevier ScienceDirect", False, False, False, "1", "Collection ID", False],
    ]


def test_normalize_swaps_school_names_within_records():
    records = [
        [
            "A",
            ["Manhattan Community College"],
            False,
            False,
            "1",
            "Collection ID",
            False,
        ],
    ]
    result = normalize_records(records)
    assert result[0][1] == ["Borough of Manhattan Community College"]
