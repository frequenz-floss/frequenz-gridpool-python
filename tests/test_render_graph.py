# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH
# pylint: disable=import-error

"""Tests for component graph rendering utilities."""

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from frequenz.client.assets import AssetsApiClient
from frequenz.client.common.microgrid import MicrogridId

from frequenz.gridpool.cli._render_graph import (
    ComponentGraphRenderer,
    RenderOptions,
    _format_category,
)

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    import networkx as nx
else:
    nx = pytest.importorskip("networkx")
    plt = pytest.importorskip("matplotlib.pyplot")


class _Category:
    def __init__(self, name: str) -> None:
        self.name = name


def test_format_category_handles_none() -> None:
    """It should default to UNKNOWN when no category is set."""
    assert _format_category(None) == "UNKNOWN"


def test_format_category_handles_named_enum() -> None:
    """It should strip the COMPONENT_CATEGORY_ prefix from enum-like values."""
    assert _format_category(_Category("COMPONENT_CATEGORY_PV")) == "PV"


def test_format_category_handles_string() -> None:
    """It should strip the prefix from string values."""
    assert _format_category("COMPONENT_CATEGORY_CHP") == "CHP"


@pytest.mark.asyncio
async def test_build_graph_populates_nodes_and_edges() -> None:
    """It should create nodes with attributes and edges from connections."""
    client = MagicMock(spec=AssetsApiClient)
    components = [
        SimpleNamespace(
            id=1, name="Meter-1", category=_Category("COMPONENT_CATEGORY_METER")
        ),
        SimpleNamespace(id=2, name=None, category=None),
    ]
    connections = [SimpleNamespace(source=1, destination=2), None]
    client.list_microgrid_electrical_components = AsyncMock(return_value=components)
    client.list_microgrid_electrical_component_connections = AsyncMock(
        return_value=connections
    )

    renderer = ComponentGraphRenderer(client)
    graph = await renderer.build_graph(MicrogridId(10))

    assert graph.has_edge(1, 2)
    assert graph.nodes[1]["name"] == "Meter-1"
    assert graph.nodes[1]["category"] == "METER"
    assert graph.nodes[2]["name"] == "2"
    assert graph.nodes[2]["category"] == "UNKNOWN"
    assert graph.nodes[2]["orig_id"] == 2


def test_compute_layout_empty_graph_returns_empty_mapping() -> None:
    """It should return an empty mapping when the graph is empty."""
    renderer = ComponentGraphRenderer(MagicMock(spec=AssetsApiClient))
    graph: nx.DiGraph[Any] = nx.DiGraph()
    assert not renderer.compute_layout(graph)


def test_compute_layout_positions_nodes_by_layer() -> None:
    """It should position nodes by layer with the root on the left."""
    renderer = ComponentGraphRenderer(MagicMock(spec=AssetsApiClient))
    graph: nx.DiGraph[Any] = nx.DiGraph()
    graph.add_edge("root", "child")

    pos = renderer.compute_layout(graph)

    assert pos["root"] == (0.0, 0.0)
    assert pos["child"] == (2.5, 0.0)


def test_select_root_prefers_nodes_with_children() -> None:
    """It should select a root node that has outgoing edges."""
    renderer = ComponentGraphRenderer(MagicMock(spec=AssetsApiClient))
    graph: nx.DiGraph[Any] = nx.DiGraph()
    graph.add_node(3)
    graph.add_node(1)
    graph.add_edge(1, 2)

    assert renderer._select_root(graph) == 1  # pylint: disable=protected-access


def test_group_by_level_adds_orphans() -> None:
    """It should append orphan nodes after the deepest layer."""
    renderer = ComponentGraphRenderer(MagicMock(spec=AssetsApiClient))
    graph: nx.DiGraph[Any] = nx.DiGraph()
    graph.add_edge("root", "child")
    graph.add_node("orphan")

    layered = renderer._group_by_level(  # pylint: disable=protected-access
        graph, "root"
    )

    assert layered[0] == ["root"]
    assert layered[1] == ["child"]
    assert layered[2] == ["orphan"]


def test_build_positions_centers_nodes_in_layer() -> None:
    """It should center nodes vertically within each layer."""
    renderer = ComponentGraphRenderer(MagicMock(spec=AssetsApiClient))
    layered_nodes = {0: ["b", "a"], 1: ["c"]}

    pos = renderer._build_positions(layered_nodes)  # pylint: disable=protected-access

    assert pos["a"] == (0.0, 0.6)
    assert pos["b"] == (0.0, -0.6)
    assert pos["c"] == (2.5, 0.0)


def test_render_writes_file_without_show(monkeypatch: pytest.MonkeyPatch) -> None:
    """It should save a figure and avoid showing it when configured."""
    renderer = ComponentGraphRenderer(MagicMock(spec=AssetsApiClient))
    graph: nx.DiGraph[Any] = nx.DiGraph()
    graph.add_node(1, name="Node-1", orig_id=1)
    pos = {1: (0.0, 0.0)}

    draw_calls: list[dict[str, object]] = []
    saved_paths: list[str] = []
    shown: list[bool] = []

    monkeypatch.setattr(nx, "draw", lambda *args, **kwargs: draw_calls.append(kwargs))
    monkeypatch.setattr(plt, "figure", lambda *args, **kwargs: None)
    monkeypatch.setattr(plt, "title", lambda *args, **kwargs: None)
    monkeypatch.setattr(plt, "tight_layout", lambda *args, **kwargs: None)
    monkeypatch.setattr(plt, "savefig", lambda path, dpi=None: saved_paths.append(path))
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: shown.append(True))

    renderer.render(graph, pos, RenderOptions(output="component_graph.png", show=False))

    assert saved_paths == ["component_graph.png"]
    assert not shown
    assert draw_calls
