# Frequenz Gridpool Library Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

<!-- Here goes notes on how to upgrade from previous versions, including deprecations and what they should be replaced with -->

## New Features

- `gridpool-cli validate <files>` checks config files offline and exits
  non-zero on the first error, to gate config-repo CI. Each file must be valid
  on its own, so a record names its own key and required fields; the files are
  then checked merged, for the cross-record checks.

- `gridpool-cli` accepts `FREQUENZ_API_KEY` and `FREQUENZ_API_SECRET` as a
  fallback pair for `ASSETS_API_AUTH_KEY` and `ASSETS_API_SIGN_SECRET`.

- Gridpools are described under `assets.gridpools`, each entry naming the
  enterprise that owns the gridpool. `AssetsConfig.find_enterprise(gridpool_id)`
  returns the configured owner.
  `gridpool-cli find-enterprise <gridpool_id> <files>` prints it from the config.
  `AssetsConfig.check` enforces the one-enterprise-per-gridpool invariant: a
  gridpool's microgrids may not disagree on it, and a declared enterprise must
  match the inferred one.

- A config derived from the Assets API now carries each microgrid's
  `enterprise_id`.

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
