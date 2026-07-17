# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

<!-- Here goes notes on how to upgrade from previous versions, including deprecations and what they should be replaced with -->

## New Features

* Added an `--inplace` flag to the `generate-config` CLI command: patches `--default` directly instead of printing to stdout, only filling in values it's missing so existing comments, field order and formatting survive untouched.
* `generate-config` now renders whole-number values (e.g. peak/rated power) as underscore-grouped ints (`1_736_680`) instead of floats (`1736680.0`), avoiding spurious diffs.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
