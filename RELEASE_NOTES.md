# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- Requires `frequenz-microgrid-component-graph` 0.6, which stops clamping the consumer
  and producer formulas. `ComponentGraph.consumer_formula()` and
  `ComponentGraph.producer_formula()` can now return values previously pinned
  to zero: a negative consumer total, or a positive producer total.

## New Features

- `generate-config` now derives a `generation` component type, with its
  `AC_POWER_ACTIVE` formula taken from `ComponentGraph.producer_formula()`, so
  the aggregated producer power is emitted alongside `consumption`.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
