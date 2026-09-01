# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Golden tests for the config format migrations."""

from pathlib import Path

import pytest

from frequenz.gridpool.config import AssetsConfig
from frequenz.gridpool.config._migrations import _CURRENT_VERSION, migrate


def test_migrate_is_a_noop_on_a_current_document() -> None:
    """A current document passes through unchanged."""
    raw = {
        "assets": {
            "version": _CURRENT_VERSION,
            "microgrids": {"1": {"microgrid_id": 1}},
        }
    }

    assert migrate(raw, Path("current.toml")) == raw


def test_migrate_rejects_a_newer_version() -> None:
    """A future document is not silently downgraded."""
    future_version = _CURRENT_VERSION + 1
    raw = {
        "assets": {
            "version": future_version,
            "microgrids": {"1": {"microgrid_id": 1}},
        }
    }

    with pytest.raises(
        ValueError, match=f"newer than supported version {_CURRENT_VERSION}"
    ):
        migrate(raw, Path("future.toml"))

    assert raw["assets"]["version"] == future_version


def test_file_without_assets_loads_empty(tmp_path: Path) -> None:
    """A file with no `assets` table loads empty and contributes nothing to a merge."""
    other = tmp_path / "app.toml"
    other.write_text('[app]\nname = "consumer"\n')
    real = tmp_path / "assets.toml"
    real.write_text(
        'assets.microgrids.1.microgrid_id = 1\nassets.microgrids.1.name = "Grid"\n'
    )

    assert AssetsConfig.load_from_files(other).microgrids == {}

    merged = AssetsConfig.load_from_files([other, real])
    assert merged.microgrids[1].name == "Grid"


def test_file_with_app_and_assets_reads_only_assets(tmp_path: Path) -> None:
    """A sibling `[app]` table next to `assets` is ignored; only `assets` is read."""
    path = tmp_path / "mixed.toml"
    path.write_text(
        "assets.microgrids.1.microgrid_id = 1\n"
        'assets.microgrids.1.name = "Grid"\n\n'
        '[app]\nname = "consumer"\n'
    )

    config = AssetsConfig.load_from_files(path)

    assert config.microgrids[1].name == "Grid"
