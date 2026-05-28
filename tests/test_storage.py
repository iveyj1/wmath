from pathlib import Path

from wmath.storage import (
    SheetMetadata,
    load_metadata,
    load_mru,
    metadata_path,
    read_sheet,
    save_metadata,
    save_mru,
    update_mru,
    write_sheet,
)


def test_sheet_round_trip(tmp_path: Path) -> None:
    sheet = tmp_path / "example.wmath"

    write_sheet(sheet, "a = 1\n")

    assert read_sheet(sheet) == "a = 1\n"


def test_metadata_round_trip(tmp_path: Path) -> None:
    sheet = tmp_path / "example.wmath"
    metadata = SheetMetadata(showValuesMode="all_assignments", valueColumnPercent=75)

    save_metadata(sheet, metadata)

    assert metadata_path(sheet) == tmp_path / "example.wmath.meta.json"
    assert load_metadata(sheet) == metadata


def test_metadata_defaults_and_clamps_invalid_values(tmp_path: Path) -> None:
    sheet = tmp_path / "example.wmath"
    metadata_path(sheet).write_text(
        '{"showValuesMode": "bad", "valueColumnPercent": 1000}', encoding="utf-8"
    )

    metadata = load_metadata(sheet)

    assert metadata.showValuesMode == "explicit"
    assert metadata.valueColumnPercent == 90.0


def test_mru_round_trip_and_update(tmp_path: Path) -> None:
    state = tmp_path / "mru.json"
    first = tmp_path / "first.wmath"
    second = tmp_path / "second.wmath"

    items = update_mru([], first)
    items = update_mru(items, second)
    items = update_mru(items, first)
    save_mru(items, state)

    loaded = load_mru(state)
    assert loaded == [first.resolve(), second.resolve()]
