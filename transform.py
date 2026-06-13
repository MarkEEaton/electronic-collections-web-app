"""Pure transforms applied to fetched records before rendering."""

SCHOOL_NAME_SWAPS = {
    "Manhattan Community College": "Borough of Manhattan Community College",
    "Fiorello H LaGuardia Community College Library": "LaGuardia Community College",
}


def swap_school_names(groups):
    """Replace outdated CUNY library names with their current names.

    ``groups`` is a list of institution names, or ``False`` when the
    collection applies to all CUNY institutions.
    """
    if not groups:
        return groups
    return [SCHOOL_NAME_SWAPS.get(name, name) for name in groups]


def normalize_records(records):
    """Swap outdated school names within each record's groups, then sort
    the records case-insensitively by public name (the first field)."""
    normalized = []
    for record in records:
        record = list(record)
        record[1] = swap_school_names(record[1])
        normalized.append(record)
    return sorted(normalized, key=lambda r: r[0].casefold())
