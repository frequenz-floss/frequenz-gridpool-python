# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- This updates the component-graph library to v0.5.0, which now needs `frequenz-client-assets` >= 0.3.1. It changes the generated per-category formulas, so regenerate stored configs with this release and review the diff.

  - The formula fallback engine was rewritten. Formulas can now use meter subtraction as a fallback, which gives better fallback coverage. The exact formula strings can differ from the previous release, even for the same graph.
  - The per-category formulas (`pv`, `battery`, `chp`, `ev`) now read the component first and use the meter as the fallback. This is the opposite of the previous order.

  See the [v0.5.0 release notes](https://github.com/frequenz-floss/frequenz-microgrid-component-graph-python/releases/tag/v0.5.0) of the component graph library for the full list of changes.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
