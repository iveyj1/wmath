from pathlib import Path

from wmath.storage import (
    SheetMetadata,
    default_mru_path,
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
        '{"showValuesMode": "bad", "valueColumnPercent": 1000, '
        '"significantFigures": 99, "scientificMagnitude": 99, "fontPointSize": 999}',
        encoding="utf-8",
    )

    metadata = load_metadata(sheet)

    assert metadata.showValuesMode == "explicit"
    assert metadata.valueColumnPercent == 90.0
    assert metadata.significantFigures == 15
    assert metadata.scientificMagnitude == 12
    assert metadata.fontPointSize == 36.0


def test_default_mru_path_uses_xdg_state_home(tmp_path: Path) -> None:
    state_home = tmp_path / "state"

    assert default_mru_path(os_name="posix", environ={"XDG_STATE_HOME": str(state_home)}) == (
        state_home / "wmath" / "mru.json"
    )


def test_default_mru_path_uses_linux_home_fallback(tmp_path: Path) -> None:
    assert default_mru_path(os_name="posix", environ={}, home=tmp_path) == (
        tmp_path / ".local" / "state" / "wmath" / "mru.json"
    )


def test_default_mru_path_uses_windows_local_app_data(tmp_path: Path) -> None:
    local_app_data = tmp_path / "LocalAppData"

    assert default_mru_path(os_name="nt", environ={"LOCALAPPDATA": str(local_app_data)}) == (
        local_app_data / "wmath" / "mru.json"
    )


def test_default_mru_path_uses_windows_home_fallback(tmp_path: Path) -> None:
    assert default_mru_path(os_name="nt", environ={}, home=tmp_path) == (
        tmp_path / "AppData" / "Local" / "wmath" / "mru.json"
    )


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
