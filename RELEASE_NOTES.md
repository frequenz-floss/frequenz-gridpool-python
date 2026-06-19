# Frequenz Gridpool Library Release Notes

## Summary

This release reworks the microgrid configuration loading API: the loaders are now module-level functions exported from `frequenz.gridpool` for loading configs from files, from the Assets API, or from both layered together. It also adds a `generate-config` CLI command.

## Upgrading

The configuration loaders are no longer `MicrogridConfig` static methods — they are module-level functions exported from `frequenz.gridpool`, and their signatures have changed:

* `MicrogridConfig.load_configs(files, dir)` → `load_configs_from_files(files)`. The `microgrid_config_dir` argument has been removed; pass an explicit list of files instead, e.g. `load_configs_from_files(list(Path(my_dir).glob("*.toml")))`. Note that the name `load_configs` now refers to the new merge wrapper (see New Features), not the file loader.
* `MicrogridConfig.load_configs_with_formulas(assets_url, assets_auth_key, assets_sign_secret, files, dir)` → `load_configs(default_files=files, assets_client=client, override_files=...)`. It now takes an `AssetsApiClient` you construct instead of raw credentials, and layers its sources by explicit precedence (default files < Assets API < override files) rather than the old "load files, then fill in missing formulas" behavior.
* The CLI dependencies (`asyncclick` and the new `tomlkit`) are no longer core dependencies; they have moved to a `cli` optional extra. Install the CLI with `pip install frequenz-gridpool[cli]` (the `render-graph` extra now pulls this in automatically).

## New Features

* Added config loading functions, exported from `frequenz.gridpool`:
   * `load_configs_from_files(...)` loads microgrid configs from one or more TOML files.
   * `load_configs_from_api(...)` loads microgrid metadata (latitude/longitude) from the Assets API and derives the per-type formulas and meter/inverter/component IDs directly from the component graph. The two steps fail independently: a microgrid whose metadata cannot be fetched is skipped, while one whose component graph cannot be derived is still returned with metadata only. Both are logged rather than aborting the whole batch.
   * `load_configs(...)` loads from up to three layered sources — default files, the Assets API, and override files — and merges them, with higher layers winning on conflicts. The microgrid IDs fetched from the Assets API can be given explicitly or are otherwise taken from the files.
* Added `merge_microgrid_configs(...)` for deep-merging two `MicrogridConfig` objects where override values take precedence and `None` does not overwrite base values.
* Added `merge_config_maps(...)` for merging two dictionaries of microgrid configs by microgrid ID.
* Added a `generate-config` CLI command that derives a microgrid config from the Assets API and prints it as TOML, optionally layering `--default` and `--override` config files by precedence (`--default` < Assets API < `--override`).

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
