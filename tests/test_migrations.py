# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Golden tests for the config format migrations."""

from pathlib import Path

import pytest

from frequenz.gridpool.config import AssetsConfig
from frequenz.gridpool.config._migrations import _CURRENT_VERSION, migrate


def test_migrate_nests_top_level_microgrids() -> None:
    """A v0 top-level document is nested under `assets.microgrids` and stamped."""
    raw = {"1": {"microgrid_id": 1, "name": "Grid"}}

    migrated = migrate(raw, Path("v0.toml"))

    assert migrated == {
        "assets": {
            "microgrids": {"1": {"microgrid_id": 1, "name": "Grid"}},
            "version": _CURRENT_VERSION,
        }
    }


def test_migrate_lifts_nested_meta() -> None:
    """A microgrid nesting fields under `meta` has them lifted onto the entry."""
    raw = {
        "assets": {"microgrids": {"1": {"meta": {"microgrid_id": 1, "name": "Grid"}}}}
    }

    migrated = migrate(raw, Path("meta.toml"))

    assert migrated["assets"]["microgrids"]["1"] == {"microgrid_id": 1, "name": "Grid"}


def test_migrate_is_a_noop_on_a_current_document() -> None:
    """A current document passes through unchanged."""
    raw = {
        "assets": {
            "version": _CURRENT_VERSION,
            "microgrids": {"1": {"microgrid_id": 1}},
        }
    }

    assert migrate(raw, Path("current.toml")) == raw


def test_migrate_rejects_mixed_layout_at_current_version() -> None:
    """Layout validation still runs when a document declares the current version."""
    raw = {
        "assets": {
            "version": _CURRENT_VERSION,
            "microgrids": {"1": {"microgrid_id": 1}},
        },
        "2": {"microgrid_id": 2},
    }

    with pytest.raises(ValueError, match="outside `assets`"):
        migrate(raw, Path("mixed.toml"))


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


def test_v0_top_level_file_loads(tmp_path: Path) -> None:
    """A v0 top-level file still loads through the public loader."""
    path = tmp_path / "v0.toml"
    path.write_text('1.microgrid_id = 1\n1.name = "Grid"\n')

    config = AssetsConfig.load_from_files(path)

    assert config.microgrids[1].name == "Grid"
    assert config.version == _CURRENT_VERSION
