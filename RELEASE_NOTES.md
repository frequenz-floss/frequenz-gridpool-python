# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- `MicrogridConfig.load_from_file` is replaced by `AssetsConfig.load_from_file`,
  which returns the whole document rather than just its microgrids:

  ```python
  configs = AssetsConfig.load_from_file(path).microgrids
  ```

  `load_configs_from_files` and `load_configs` are unchanged.

## New Features

- `AssetsConfig` gives the `assets` namespace a type, so the entities still to
  come are added as fields rather than as more dict lookups. Entries are checked
  against the ID they are filed under wherever the class is loaded, not only via
  `load_from_file`.

  Entity tables a version does not know are ignored with a warning, so a reader
  keeps working against files that already carry newer entities.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
