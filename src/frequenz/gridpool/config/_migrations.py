# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Format migrations for raw config documents.

Loading validates `assets.version` and stamps the current version, so a file
written for a newer reader is rejected rather than silently misread. Each
migration step rewrites the raw `dict` before it is loaded into the typed
model; steps are self-detecting and idempotent, so the `version` field does not
gate whether a step runs. No legacy layouts remain, so `_STEPS` is empty.
"""

from pathlib import Path
from typing import Any, Callable

_CURRENT_VERSION = 1


def migrate(raw: dict[str, Any], source: Path) -> dict[str, Any]:
    """Migrate a raw config document to the current format.

    Reads and validates `assets.version` (absent means the oldest, `0`), applies
    every self-detecting step, and stamps the current version. The version sits
    inside `assets` so it tracks the assets format alone, not the whole document.

    Args:
        raw: The raw document as parsed from a file.
        source: The file it was parsed from, named in error messages.

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


_STEPS: list[tuple[int, Callable[[dict[str, Any], Path], dict[str, Any]]]] = []
"""Migration steps as `(from_version, step)`, oldest first."""
