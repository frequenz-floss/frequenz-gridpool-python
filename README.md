# Frequenz Gridpool Library

[![Build Status](https://github.com/frequenz-floss/frequenz-gridpool-python/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/frequenz-gridpool-python/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/frequenz-gridpool)](https://pypi.org/project/frequenz-gridpool/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/frequenz-gridpool-python/)

## Introduction

High-level interface to grid pools for the Frequenz platform.

TODO(cookiecutter): Improve the README file

## Supported Platforms

The following platforms are officially supported (tested):

- **Python:** 3.11
- **Operating System:** Ubuntu Linux 20.04
- **Architectures:** amd64, arm64

## CLI

This package ships the `gridpool-cli` command with three subcommands.

### Setup

Set the Assets API credentials before running the CLI:

```bash
export ASSETS_API_URL="grpc://..."
export ASSETS_API_AUTH_KEY="..."
export ASSETS_API_SIGN_SECRET="..."
```

### Print component formulas

```bash
gridpool-cli print-formulas <microgrid_id>
```

Optional prefix formatting:

```bash
gridpool-cli print-formulas <microgrid_id> --prefix "{microgrid_id}.{component}"
```

### Render component graph

Rendering requires optional dependencies. Install with:

```bash
pip install frequenz-gridpool[render-graph]
```

```bash
gridpool-cli render-graph <microgrid_id>
```

To save without opening a window:

```bash
gridpool-cli render-graph <microgrid_id> --no-show --output component_graph.png
```

### Generate microgrid config

Derive metadata, formulas and component IDs for one or more microgrids from the
Assets API and print them as dotted-key TOML to stdout:

```bash
gridpool-cli generate-config <microgrid_id> [<microgrid_id> ...]
```

Redirect stdout to save the result:

```bash
gridpool-cli generate-config <microgrid_id> > microgrid.toml
```

You can layer existing config files with the Assets API by precedence
(`--default` < Assets API < `--override`). Values from a `--default` file are
overridden by the API, while a `--override` file keeps its own values and the
API only fills the gaps:

```bash
gridpool-cli generate-config <microgrid_id> \
    --default defaults.toml \
    --override overrides.toml > microgrid.toml
```

If no microgrid IDs are given, they are taken from the supplied files:

```bash
gridpool-cli generate-config --override existing.toml > microgrid.toml
```

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).
