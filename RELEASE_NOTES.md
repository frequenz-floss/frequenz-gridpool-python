# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- Microgrid config files should nest their entries under `assets.microgrids`:

  ```toml
  assets.microgrids.23.meta.name = "..."
  ```

  Bare microgrid IDs at the top level still load but log a deprecation warning,
  and support for them will be removed. The namespace keeps generated inventory
  data apart from operator settings under `app.*`, so a config file can carry
  both without its keys colliding.

  A file mixing both layouts is rejected.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
