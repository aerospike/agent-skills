"""The reference-file parser must treat only the template's five labels as
section boundaries. Bold content lines are content, not headings."""

from scripts.skills_compile.skillsrc import labeled_sections


def test_bolded_url_line_does_not_split_the_rule():
    body = (
        "**Rule**\n\n"
        "The full process lives in the\n"
        "**`https://github.com/aerospike/data-modeling-guide`**\n"
        "repository. Fetch it and follow its checklist.\n\n"
        "**Prefer**\n\n"
        "- Reading current values from the guide\n"
    )

    sections = labeled_sections(body)

    assert set(sections) == {"Rule", "Prefer"}
    assert "data-modeling-guide" in sections["Rule"]
    assert sections["Rule"].endswith("Fetch it and follow its checklist.")


def test_bolded_enumerated_headings_stay_inside_the_rule():
    body = (
        "**Rule**\n\n"
        "Each failure mode below has a detection test.\n\n"
        "**1. Record granularity from the entity list.**\n"
        "*Detect:* count the sets.\n\n"
        "**2. Secondary indexes as the primary query mechanism.**\n"
        "*Detect:* list every access pattern.\n\n"
        "**Avoid**\n\n"
        "- Running these only at the end\n"
    )

    sections = labeled_sections(body)

    assert set(sections) == {"Rule", "Avoid"}
    assert "1. Record granularity" in sections["Rule"]
    assert "2. Secondary indexes" in sections["Rule"]


def test_bolded_gotcha_heading_stays_inside_the_avoid_list():
    body = (
        "**Avoid**\n\n"
        "- Reading a whole record when one bin will do\n\n"
        "**Gotcha: bin-scoped ops vs whole-record reads**\n"
        "A bin-scoped operation still reads the whole record from device.\n"
    )

    sections = labeled_sections(body)

    assert set(sections) == {"Avoid"}
    assert "Gotcha" in sections["Avoid"]


def test_all_five_canonical_labels_still_split():
    body = (
        "**Rule**\n\nR\n\n"
        "**Why**\n\nW\n\n"
        "**Prefer**\n\n- p\n\n"
        "**Avoid**\n\n- a\n\n"
        "**See also**\n\n- s\n"
    )

    assert set(labeled_sections(body)) == {
        "Rule",
        "Why",
        "Prefer",
        "Avoid",
        "See also",
    }
