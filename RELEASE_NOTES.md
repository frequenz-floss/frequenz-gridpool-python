# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- Requires `frequenz-microgrid-component-graph` 0.6, which stops clamping the consumer
  and producer formulas. `ComponentGraph.consumer_formula()` and
  `ComponentGraph.producer_formula()` can now return values previously pinned
  to zero: a negative consumer total, or a positive producer total.

## New Features

- Automatically generate component formulas for the `AC_ENERGY_ACTIVE`, `AC_ENERGY_ACTIVE_CONSUMED`, and `AC_ENERGY_ACTIVE_DELIVERED` metrics when deriving microgrid configuration from the Assets API, in addition to the existing `AC_POWER_ACTIVE` formulas.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
