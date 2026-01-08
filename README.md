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

This package ships the `gridpool-cli` command with two subcommands.

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

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).
