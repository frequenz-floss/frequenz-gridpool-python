# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Tests for the raw-table merge helper backing the config loaders."""

from frequenz.gridpool.config._assets import _deep_merge


def test_override_wins() -> None:
    """A scalar in the override replaces the base value."""
    assert _deep_merge({"name": "Base"}, {"name": "New"}) == {"name": "New"}


def test_none_does_not_nullify() -> None:
    """A None override is skipped so the base value survives.

    This is what lets a dumped-object layer (e.g. the Assets API) leave a field
    unset without clobbering a value a lower layer provided.
    """
    base = {"name": "Base", "enterprise_id": 5, "longitude": 20.0}
    override = {"name": "New", "enterprise_id": None, "longitude": None}

    assert _deep_merge(base, override) == {
        "name": "New",
        "enterprise_id": 5,
        "longitude": 20.0,
    }


def test_nested_tables_merge_recursively() -> None:
    """Nested tables merge recursively, keeping base-only keys."""
    base = {"pv": {"meter": [1, 2]}, "battery": {"inverter": [3, 4]}}
    override = {"pv": {"formula": "#1"}, "grid": {"meter": [9]}}

    assert _deep_merge(base, override) == {
        "pv": {"meter": [1, 2], "formula": "#1"},
        "battery": {"inverter": [3, 4]},
        "grid": {"meter": [9]},
    }


def test_inputs_are_not_mutated() -> None:
    """Merging returns a new table without mutating its inputs."""
    base = {"pv": {"meter": [1, 2]}}
    override = {"pv": {"formula": "#1"}}

    _deep_merge(base, override)

    assert base == {"pv": {"meter": [1, 2]}}
    assert override == {"pv": {"formula": "#1"}}


def test_ids_unique_to_one_layer_pass_through() -> None:
    """Shared IDs merge; IDs present in only one layer pass through unchanged.

    The map-merge the loaders used to do by hand now falls out of the nested
    `assets.microgrids.<id>` structure for free.
    """
    base = {"microgrids": {"1": {"name": "Base One"}, "2": {"name": "Base Two"}}}
    override = {
        "microgrids": {"1": {"name": "Override One"}, "3": {"name": "Override Three"}}
    }

    assert _deep_merge(base, override) == {
        "microgrids": {
            "1": {"name": "Override One"},
            "2": {"name": "Base Two"},
            "3": {"name": "Override Three"},
        }
    }
