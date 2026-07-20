# Frequenz Gridpool Library Release Notes

## Summary

This release updates the microgrid component graph library to v0.5.0 and adds a way to configure how the component graph is built.

## Upgrading

* The per-category formulas (`pv`, `battery`, `chp`, `ev`) now read the component first and use the meter as the fallback. This is the opposite of the old order, and it changes the generated config. Regenerate stored configs with this release and review the diff.
* To keep the old order, pass `ComponentGraphConfig(prefer_meters_in_component_formulas=True)` to `load_configs`, `load_configs_from_api` or `ComponentGraphGenerator`, or use the new `--prefer-meters-in-component-formulas` flag of the CLI.
* The update brings more changes, for example to the `consumption` formula and to the graph validation error messages. See the [v0.5.0 release notes](https://github.com/frequenz-floss/frequenz-microgrid-component-graph-python/releases/tag/v0.5.0) of the component graph library for the full list.

## New Features

* `load_configs` and `load_configs_from_api` take a `component_graph_config` argument, and `ComponentGraphGenerator` takes it as `config`. It controls how the component graph is built and how its formulas are generated. `ComponentGraphConfig` and `FormulaOverrides` are re-exported from `frequenz.gridpool` and `frequenz.gridpool.config`.
* The `generate-config` and `print-formulas` CLI commands take a `--prefer-meters-in-component-formulas` flag, which reads the meter before the component in the per-category formulas.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
