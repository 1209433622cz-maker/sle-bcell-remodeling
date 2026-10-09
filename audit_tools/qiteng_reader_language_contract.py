"""Contract for the authorized QiTeng reader-language-only Supplementary delta."""

from pathlib import Path


READER_LANGUAGE_REPLACEMENTS = (
    ("Prespecified 12-gene IFN/ISG arm", "Frozen 12-gene IFN/ISG arm", 3),
    ("BH across three prespecified base contrasts", "BH across three frozen base contrasts", 1),
    ("Four prespecified programs", "Four frozen programs", 1),
    ("Additional sensitivity", "Post-freeze sensitivity", 1),
    (
        "removal of the prespecified 12-gene IFN/ISG positive arm",
        "removal of the frozen 12-gene IFN/ISG positive arm",
        1,
    ),
    (
        "Percentage of matched targets retained after each depletion",
        "Percentage of frozen matched targets retained after each depletion",
        1,
    ),
)


def assert_authorized_supplement_delta(testcase, current: Path, parent: Path) -> None:
    """Require the current source to differ only by the registered reader wording."""
    observed = current.read_text(encoding="utf-8")
    reconstructed = observed
    for reader_text, parent_text, expected_count in READER_LANGUAGE_REPLACEMENTS:
        testcase.assertEqual(reconstructed.count(reader_text), expected_count, reader_text)
        reconstructed = reconstructed.replace(reader_text, parent_text)
    testcase.assertEqual(reconstructed, parent.read_text(encoding="utf-8"))
