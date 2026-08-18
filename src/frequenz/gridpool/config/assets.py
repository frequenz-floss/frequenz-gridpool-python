# License: MIT
# Copyright © 2026 Frequenz Energy-as-a-Service GmbH

"""Data model for the `assets` config namespace."""

import logging
import tomllib
from dataclasses import field
from pathlib import Path
from typing import Any, ClassVar, Self, Type

import marshmallow
from marshmallow import Schema
from marshmallow_dataclass import dataclass

from .microgrid import MicrogridConfig

_logger = logging.getLogger(__name__)


@dataclass
class AssetsConfig:
    """Entities described by a config document, keyed by their ID."""

    microgrids: dict[str, MicrogridConfig] = field(default_factory=dict)
    """Microgrids, keyed by microgrid ID."""

    class Meta:
        """Ignore entity tables this version does not know about.

        A reader must keep working against files that already carry entities
        added after it, so unknown tables are skipped rather than rejected.
        `_warn_unknown_entities` reports them, so a mistyped table is still
        visible instead of silently loading as empty.
        """

        unknown = marshmallow.EXCLUDE

    Schema: ClassVar[Type[Schema]] = Schema

    def __post_init__(self) -> None:
        """Check that each entry is filed under its own ID.

        Raises:
            ValueError: If a key is not a numeric microgrid ID, or does not
                match its entry's `meta.microgrid_id`.
        """
        for mid, cfg in self.microgrids.items():
            if not mid.isdigit():
                raise ValueError(f"Microgrid ID key must be numeric, got {mid}")
            if int(cfg.meta.microgrid_id) != int(mid):
                raise ValueError(
                    f"Microgrid ID mismatch: key {mid} != {cfg.meta.microgrid_id}"
                )

    @classmethod
    def _warn_unknown_entities(cls, assets: dict[str, Any], source: Path) -> None:
        """Warn about entity tables that this version drops on load."""
        if unknown := sorted(set(assets) - set(cls.Schema().fields)):
            _logger.warning(
                "%s: ignoring unknown entity tables under `assets`: %s",
                source,
                ", ".join(unknown),
            )

    @classmethod
    def load_from_file(cls, config_path: Path) -> Self:
        """Load and validate a config document from a TOML file.

        Entries live under `assets`. A document without an `assets` table is
        read in the deprecated layout, where the microgrid entries sit at the
        top level.

        Args:
            config_path: The path to the TOML configuration file.

        Returns:
            The loaded configuration.

        Raises:
            TypeError: If `assets` is not a table.
            ValueError: If both layouts are present, which means a
                half-migrated file rather than a merge.
        """
        with config_path.open("rb") as f:
            data: dict[str, Any] = tomllib.load(f)

        if "assets" not in data:
            _logger.warning(
                "%s: top-level microgrid IDs are deprecated, "
                "nest the entries under `assets.microgrids` instead.",
                config_path,
            )
            data = {"assets": {"microgrids": data}}

        assets = data["assets"]
        if not isinstance(assets, dict):
            raise TypeError(
                f"{config_path}: `assets` must be a table, got {type(assets)}"
            )

        if unprefixed := sorted(k for k in data if k != "assets"):
            raise ValueError(
                f"{config_path}: keys {unprefixed} sit outside `assets` while the "
                "file already has an `assets` table; move them under "
                "`assets.microgrids`."
            )

        cls._warn_unknown_entities(assets, config_path)
        loaded = cls.Schema().load(assets)
        assert isinstance(loaded, cls)
        return loaded
