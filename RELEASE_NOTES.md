# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

<!-- Here goes notes on how to upgrade from previous versions, including deprecations and what they should be replaced with -->

## New Features

- If there are unconnected breakers at a site, they are now hidden from the component graph.  If there are breakers with connections to other components, they are still sent to the component graph.  This is a temporary measure until the graph traversal supports breakers.

## Bug Fixes

- Fixed auto-formula population to only fill formulas for component types already present in a microgrid configuration. This prevents creating placeholder entries with `None` formulas for component types that are not configured.
