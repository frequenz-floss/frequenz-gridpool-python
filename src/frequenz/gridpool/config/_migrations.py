# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Format migrations for raw config documents.

Each step rewrites the raw `dict` a file parses to, before it is loaded into the
typed model. Steps are self-detecting and idempotent, so the `version` field
does not gate whether a step runs; it only records how old a file may be, which
bounds when a step may be dropped.
"""

import logging
from pathlib import Path
from typing import Any, Callable

_logger = logging.getLogger(__name__)

_CURRENT_VERSION = 1


def migrate(raw: dict[str, Any], source: Path) -> dict[str, Any]:
    """Migrate a raw config document to the current format.

    Reads and validates `assets.version` (absent means the oldest, `0`), applies
    every self-detecting step, and stamps the current version. The version sits
    inside `assets` so it tracks the assets format alone, not the whole document.

    Args:
        raw: The raw document as parsed from a file.
        source: The file it was parsed from, for warnings and errors.

    Returns:
        The document in the current format.

    Raises:
        TypeError: If `assets.version` is not an integer.
        ValueError: If `assets.version` is outside the supported range.
    """
    assets = raw.get("assets")
    version = assets.get("version", 0) if isinstance(assets, dict) else 0
    if not isinstance(version, int) or isinstance(version, bool):
        raise TypeError(f"{source}: `assets.version` must be an integer")
    if version < 0:
        raise ValueError(f"{source}: `assets.version` must not be negative")
    if version > _CURRENT_VERSION:
        raise ValueError(
            f"{source}: assets version {version} is newer than supported "
            f"version {_CURRENT_VERSION}"
        )

    for _, step in _STEPS:
        raw = step(raw, source)
    assets = raw.get("assets")
    if isinstance(assets, dict):
        assets["version"] = _CURRENT_VERSION
    return raw


def _nest_top_level_microgrids(raw: dict[str, Any], source: Path) -> dict[str, Any]:
    """Wrap deprecated top-level microgrid entries under `assets.microgrids`.

    Args:
        raw: The raw document.
        source: The file it was parsed from.

    Returns:
        The document with its entries under `assets`.

    Raises:
        ValueError: If both layouts are present, a half-migrated file rather
            than a merge.
    """
    if "assets" in raw:
        stray = sorted(k for k in raw if k != "assets")
        if stray:
            raise ValueError(
                f"{source}: keys {stray} sit outside `assets` while the file "
                "already has an `assets` table; move them under `assets.microgrids`."
            )
        return raw

    _logger.warning(
        "%s: top-level microgrid IDs are deprecated, "
        "nest the entries under `assets.microgrids` instead.",
        source,
    )
    return {"assets": {"microgrids": dict(raw)}}


def _lift_microgrid_meta(raw: dict[str, Any], source: Path) -> dict[str, Any]:
    """Merge a deprecated nested `meta` table onto its microgrid entry.

    Earlier files nested a microgrid's fields under `meta`; they now sit
    directly on the entry.

    Args:
        raw: The raw document.
        source: The file it was parsed from.

    Returns:
        The document with microgrid fields directly on each entry.

    Raises:
        TypeError: If a `meta` value is not a table.
        ValueError: If a field is set both under `meta` and on the entry.
    """
    assets = raw.get("assets")
    if not isinstance(assets, dict):
        return raw
    microgrids = assets.get("microgrids")
    if not isinstance(microgrids, dict):
        return raw
    for mid, entry in microgrids.items():
        if not isinstance(entry, dict) or "meta" not in entry:
            continue
        meta = entry.pop("meta")
        if not isinstance(meta, dict):
            raise TypeError(f"{source}: microgrid {mid} `meta` must be a table")
        _logger.warning(
            "%s: microgrid %s nests fields under `meta`; that is deprecated, "
            "set them directly on the entry instead.",
            source,
            mid,
        )
        for key, value in meta.items():
            if key in entry:
                raise ValueError(
                    f"{source}: microgrid {mid} sets `{key}` both under `meta` "
                    "and directly; keep only the direct one"
                )
            entry[key] = value
    return raw


_STEPS: list[tuple[int, Callable[[dict[str, Any], Path], dict[str, Any]]]] = [
    (0, _nest_top_level_microgrids),
    (0, _lift_microgrid_meta),
]
"""Migration steps as `(from_version, step)`, oldest first."""
