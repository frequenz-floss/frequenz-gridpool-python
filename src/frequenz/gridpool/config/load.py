# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Loading and merging of microgrid configurations."""

import logging
from pathlib import Path

from frequenz.client.assets import AssetsApiClient
from frequenz.client.common.microgrid import MicrogridId

from .._graph_generator import ComponentGraphGenerator
from .microgrid import (
    ComponentTypeConfig,
    Metadata,
    MicrogridConfig,
    merge_config_maps,
)

_logger = logging.getLogger(__name__)


async def load_configs(
    default_files: str | Path | list[str | Path] | None = None,
    assets_client: AssetsApiClient | None = None,
    override_files: str | Path | list[str | Path] | None = None,
    microgrid_ids: list[int] | None = None,
) -> dict[str, "MicrogridConfig"]:
    """Load configs from up to three sources and merge them in layers.

    Combines up to three sources, listed here from lowest to highest
    precedence: a *default* config file layer, the Assets API, and an
    *override* config file layer.  Higher layers win on conflicts, while
    lower layers fill in anything the higher ones leave unset.  This lets
    callers pick a strategy by choosing which sources to pass, for example:

    - `default_files` + `assets_client`: files provide defaults that the
      Assets API overrides.
    - `assets_client` + `override_files`: the Assets API provides the base
      that files override.
    - all three: the Assets API sits between a default and an override file
      layer.

    The microgrid IDs fetched from the Assets API are `microgrid_ids` when
    given, otherwise the IDs found in the default and override files.  This
    lets the Assets API layer be used even when no files are given.

    Args:
        default_files:
            Optional path or list of paths to config files forming the
            lowest-precedence layer.
        assets_client:
            Optional Assets API client.  When given, microgrid metadata and
            formulas are fetched and layered above the default files.
        override_files:
            Optional path or list of paths to config files forming the
            highest-precedence layer.
        microgrid_ids:
            Optional explicit microgrid IDs to fetch from the Assets API.
            When given, these replace the IDs derived from the files, so the
            Assets API layer can be used without any files.

    Returns:
        dict[str, MicrogridConfig]:
            Mapping from microgrid ID (as string) to the merged
            `MicrogridConfig` instance.

    Raises:
        ValueError: If none of the three sources is provided, or if
            `microgrid_ids` is given without an `assets_client`.
    """
    if default_files is None and assets_client is None and override_files is None:
        raise ValueError("At least one config source must be provided.")

    if microgrid_ids is not None and assets_client is None:
        raise ValueError("microgrid_ids requires an assets_client.")

    configs: dict[str, MicrogridConfig] = {}
    if default_files is not None:
        configs = load_configs_from_files(
            microgrid_config_files=default_files,
        )

    override_configs: dict[str, MicrogridConfig] = {}
    if override_files is not None:
        override_configs = load_configs_from_files(
            microgrid_config_files=override_files,
        )

    if assets_client is not None:
        if microgrid_ids is None:
            microgrid_ids = sorted({int(mid) for mid in (*configs, *override_configs)})
        assets_configs = await load_configs_from_api(
            assets_client=assets_client,
            microgrid_ids=microgrid_ids,
        )
        configs = merge_config_maps(base=configs, override=assets_configs)

    return merge_config_maps(base=configs, override=override_configs)


def load_configs_from_files(
    microgrid_config_files: str | Path | list[str | Path] | None = None,
) -> dict[str, "MicrogridConfig"]:
    """Load multiple microgrid configurations from one or more files.

    Configs for a single microgrid are expected to be in a single file.
    Later files with the same microgrid ID will overwrite the previous configs.

    Args:
        microgrid_config_files: Path to a single microgrid config file or list of paths.

    Returns:
        Dictionary of single microgrid formula configs with microgrid IDs as keys.

    Raises:
        ValueError: If no config files are provided, or if no config files are found.
    """
    if microgrid_config_files is None:
        raise ValueError(
            "No microgrid config files provided. Please provide at least one."
        )

    config_files: list[Path] = []

    if microgrid_config_files:
        if isinstance(microgrid_config_files, str):
            config_files = [Path(microgrid_config_files)]
        elif isinstance(microgrid_config_files, Path):
            config_files = [microgrid_config_files]
        elif isinstance(microgrid_config_files, list):
            config_files = [Path(f) for f in microgrid_config_files]

    if len(config_files) == 0:
        raise ValueError(
            "No microgrid config files found. "
            "Please provide at least one valid config file."
        )

    microgrid_configs: dict[str, "MicrogridConfig"] = {}

    for config_path in config_files:
        if not config_path.is_file():
            _logger.warning("Config path %s is not a file, skipping.", config_path)
            continue

        mcfgs = MicrogridConfig.load_from_file(config_path)
        microgrid_configs.update({str(key): value for key, value in mcfgs.items()})

    return microgrid_configs


async def load_configs_from_api(
    assets_client: AssetsApiClient,
    microgrid_ids: list[int],
    populate_formulas: bool = True,
) -> dict[str, "MicrogridConfig"]:
    """Load microgrid configs with location metadata from the Assets API.

    Fetches each microgrid's location (latitude, longitude) and optionally
    populates formulas from the component graph.  This is the canonical
    single-source loader for both metadata and formulas so that callers
    (e.g. the forecast pipeline) do not have to re-implement this logic.

    Args:
        assets_client:
            Assets API client used to fetch microgrid metadata and the
            component graph.
        microgrid_ids:
            List of microgrid IDs to load configurations for.
        populate_formulas:
            When `True` (default), formulas are derived from the component
            graph and written into each config via
            `_populate_missing_formulas`.  Set to `False` to load
            metadata only.

    Returns:
        dict[str, MicrogridConfig]:
            Mapping from microgrid ID (as string) to the populated
            `MicrogridConfig` instance. Microgrids that could not be loaded
            are logged as warnings and omitted, so the returned mapping may
            cover fewer microgrids than were requested.
    """
    configs: dict[str, MicrogridConfig] = {}
    for microgrid_id in microgrid_ids:
        try:
            cfg = await _build_config_from_metadata(assets_client, microgrid_id)
            if populate_formulas:
                await _populate_missing_formulas(
                    microgrid_id=microgrid_id,
                    config=cfg,
                    assets_client=assets_client,
                )
        except Exception as exc:  # pylint: disable=broad-except
            _logger.warning(
                "Failed to load microgrid %s from the Assets API: %s",
                microgrid_id,
                exc,
            )
            continue
        configs[str(microgrid_id)] = cfg

    return configs


async def _build_config_from_metadata(
    assets_client: AssetsApiClient, microgrid_id: int
) -> MicrogridConfig:
    """Build a base config for a microgrid from its Assets API metadata.

    Fetches the microgrid's location and returns a `MicrogridConfig` carrying
    only metadata; formulas are derived separately.

    Args:
        assets_client: Assets API client used to fetch the microgrid.
        microgrid_id: ID of the microgrid to fetch.

    Returns:
        A `MicrogridConfig` with metadata from the Assets API.
    """
    mgrid = await assets_client.get_microgrid(MicrogridId(microgrid_id))
    location = mgrid.location if mgrid.location else None
    return MicrogridConfig(
        meta=Metadata(
            microgrid_id=microgrid_id,
            latitude=location.latitude if location else None,
            longitude=location.longitude if location else None,
        )
    )


def _is_zero_formula(formula: str) -> bool:
    """Return whether a derived formula is empty or a constant zero.

    Component types absent from a microgrid yield an empty formula or one that
    is just a zero constant (e.g. `0.0`), which is not worth storing.
    """
    stripped = formula.strip()
    if not stripped:
        return True
    try:
        return float(stripped) == 0.0
    except ValueError:
        return False


async def _populate_missing_formulas(
    microgrid_id: int,
    config: "MicrogridConfig",
    assets_client: AssetsApiClient,
    component_types: set[str] | None = None,
) -> None:
    """Populate missing component formulas from the assets API graph.

    Builds a component graph for the given microgrid and derives default formulas
    for common component types such as consumption, grid, PV, battery, CHP, and
    EV charging. Existing formulas already present in the configuration are
    preserved; only missing component-type entries or missing metric formulas
    are filled in.

    Args:
        microgrid_id:
            Identifier of the microgrid whose component graph should be used to
            derive formulas.
        config:
            Microgrid configuration object to update in place.
        assets_client:
            Assets API client used to fetch the component graph.
        component_types:
            Set of component types to consider when populating formulas. When
            `None` (the default), every component type a formula can be derived
            for is considered.

    Returns:
        None. The configuration is modified in place.

    Notes:
        - Existing formulas in `config` are never overwritten.
        - For missing component types, a new `ComponentTypeConfig` is created.
        - The derived formula is assigned to the `AC_POWER_ACTIVE` metric key
        for a given component type when missing.
    """
    cgg = ComponentGraphGenerator(assets_client)
    graph = await cgg.get_component_graph(MicrogridId(microgrid_id))

    auto_formulas = {
        "consumption": graph.consumer_formula(),
        "grid": graph.grid_formula(),
        "pv": graph.pv_formula(None),
        "battery": graph.battery_formula(None),
        "chp": graph.chp_formula(None),
        "ev": graph.ev_charger_formula(None),
    }

    for ctype, formula in auto_formulas.items():
        if component_types is not None and ctype not in component_types:
            continue

        # Skip component types, whose derived formula
        # is empty or evaluates to a constant zero.
        if _is_zero_formula(formula):
            continue

        cfg = config.ctype.get(ctype)
        if cfg is None:
            cfg = ComponentTypeConfig()
            config.ctype[ctype] = cfg

        if cfg.formula is None:
            cfg.formula = {}

        if "AC_POWER_ACTIVE" not in cfg.formula:
            cfg.formula["AC_POWER_ACTIVE"] = formula
