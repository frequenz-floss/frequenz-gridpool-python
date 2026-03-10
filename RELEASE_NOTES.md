# Frequenz Gridpool Library Release Notes

## Summary

This release adds default formulas for AC energy metrics when they are not
explicitly configured.

## Upgrading


## New Features

* Added default summation formulas for `AC_ENERGY_ACTIVE`,
  `AC_ENERGY_ACTIVE_CONSUMED`, and `AC_ENERGY_ACTIVE_DELIVERED` when formulas are
  not provided. The defaults are built from the component IDs configured for the
  component type.

## Bug Fixes

