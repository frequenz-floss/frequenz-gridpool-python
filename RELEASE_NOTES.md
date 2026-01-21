# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

* The minimum required version of `frequenz-microgrid-component-graph` is now `v0.3.4`.

## New Features

* Added `gridpool-cli render-graph` to visualize microgrid component graphs using the
  Assets API credentials (`ASSETS_API_URL`, `ASSETS_API_AUTH_KEY`, and
  `ASSETS_API_SIGN_SECRET`).

## Bug Fixes

- Fixed component graph rendering so children follow the vertical order of their parents, keeping upper-level branches above lower ones in the layered layout.