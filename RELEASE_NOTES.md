# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

<!-- Here goes notes on how to upgrade from previous versions, including deprecations and what they should be replaced with -->

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

- `load_configs()` and `load_configs_from_files()` now accept directory paths in
  addition to individual TOML files. When a directory is provided, all
  `*.toml` files in that directory are loaded in sorted order.
