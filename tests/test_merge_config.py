# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Tests for the config merge helpers."""

from typing import Any

from frequenz.gridpool.config import (
    MicrogridConfig,
    merge_config_maps,
    merge_microgrid_configs,
)


def _make_config(mid: int, entry: dict[str, Any]) -> MicrogridConfig:
    """Build a single MicrogridConfig from a table entry.

    Args:
        mid: The microgrid ID; also used as the table key.
        entry: The microgrid config body (meta, ctype, ...).

    Returns:
        The parsed MicrogridConfig instance.
    """
    meta = {"microgrid_id": mid, **entry.get("meta", {})}
    # pylint: disable=protected-access
    return MicrogridConfig._load_table_entries({str(mid): {**entry, "meta": meta}})[
        str(mid)
    ]


def test_merge_override_wins() -> None:
    """Override scalar fields take precedence over the base."""
    base = _make_config(1, {"meta": {"name": "Base Grid", "latitude": 10.0}})
    override = _make_config(1, {"meta": {"name": "New Grid", "latitude": 99.0}})

    merged = merge_microgrid_configs(base, override)

    assert merged.meta is not None
    assert merged.meta.name == "New Grid"
    assert merged.meta.latitude == 99.0


def test_merge_none_does_not_nullify() -> None:
    """Fields absent from the override retain their base values."""
    base = _make_config(
        1,
        {"meta": {"name": "Base Grid", "enterprise_id": 5, "longitude": 20.0}},
    )
    # Override only sets the name; enterprise_id/longitude are None and skipped.
    override = _make_config(1, {"meta": {"name": "New Grid"}})

    merged = merge_microgrid_configs(base, override)

    assert merged.meta is not None
    assert merged.meta.name == "New Grid"
    assert merged.meta.enterprise_id == 5
    assert merged.meta.longitude == 20.0


def test_merge_nested_ctype() -> None:
    """Nested dicts are merged recursively, keeping base-only keys."""
    base = _make_config(
        1,
        {
            "ctype": {
                "pv": {"meter": [1, 2]},
                "battery": {"inverter": [3, 4]},
            }
        },
    )
    override = _make_config(
        1,
        {
            "ctype": {
                "pv": {"formula": {"AC_POWER_ACTIVE": "#1"}},
                "grid": {"meter": [9]},
            }
        },
    )

    merged = merge_microgrid_configs(base, override)

    # pv: base meter retained, override formula added.
    assert merged.ctype["pv"].meter == [1, 2]
    assert merged.ctype["pv"].formula == {"AC_POWER_ACTIVE": "#1"}
    # battery: present only in base, kept unchanged.
    assert merged.ctype["battery"].inverter == [3, 4]
    # grid: present only in override, added.
    assert merged.ctype["grid"].meter == [9]


def test_merge_does_not_mutate_inputs() -> None:
    """Merging returns a new config without mutating base or override."""
    base = _make_config(1, {"meta": {"name": "Base Grid"}})
    override = _make_config(1, {"meta": {"name": "New Grid"}})

    merge_microgrid_configs(base, override)

    assert base.meta is not None and base.meta.name == "Base Grid"
    assert override.meta is not None and override.meta.name == "New Grid"


def test_merge_config_maps() -> None:
    """Maps are merged per ID; IDs unique to one map are passed through."""
    base = {
        "1": _make_config(1, {"meta": {"name": "Base One"}}),
        "2": _make_config(2, {"meta": {"name": "Base Two"}}),
    }
    override = {
        "1": _make_config(1, {"meta": {"name": "Override One"}}),
        "3": _make_config(3, {"meta": {"name": "Override Three"}}),
    }

    merged = merge_config_maps(base, override)

    assert set(merged) == {"1", "2", "3"}
    # Shared ID: override wins.
    assert merged["1"].meta is not None and merged["1"].meta.name == "Override One"
    # Base-only ID: unchanged.
    assert merged["2"].meta is not None and merged["2"].meta.name == "Base Two"
    # Override-only ID: included.
    assert merged["3"].meta is not None and merged["3"].meta.name == "Override Three"
