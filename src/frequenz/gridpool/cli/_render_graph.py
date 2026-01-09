# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH
# pylint: disable=import-error

"""Render component graphs via the Assets API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from frequenz.client.assets import AssetsApiClient
from frequenz.client.common.microgrid import MicrogridId


def _format_category(category: Any) -> str:
    """Normalize a component category into a short display label."""
    if category is None:
        return "UNKNOWN"
    if hasattr(category, "name"):
        return str(category.name).replace("COMPONENT_CATEGORY_", "")
    return str(category).replace("COMPONENT_CATEGORY_", "")


def _require_networkx() -> Any:
    try:
        # pylint: disable=import-outside-toplevel
        import networkx as nx
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Rendering requires optional dependencies. Install "
            "`frequenz-gridpool[render-graph]`."
        ) from exc
    return nx


def _require_matplotlib() -> Any:
    try:
        # pylint: disable=import-outside-toplevel
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Rendering requires optional dependencies. Install "
            "`frequenz-gridpool[render-graph]`."
        ) from exc
    return plt


@dataclass(frozen=True)
class RenderOptions:
    """Rendering options for component graphs."""

    output: str
    show: bool = True
    figsize: tuple[int, int] = (15, 10)
    title: str = "Microgrid Component Graph"


class ComponentGraphRenderer:
    """Build and render component graphs for a microgrid."""

    def __init__(self, client: AssetsApiClient) -> None:
        """Initialize the renderer.

        Args:
            client: API client used to fetch microgrid components and their connections.
        """
        self._client = client

    async def build_graph(self, microgrid_id: MicrogridId) -> Any:
        """Build a directed graph representing the microgrid electrical topology.

        Fetches electrical components and their connections for the given microgrid and
        constructs a directed graph where nodes represent components and edges represent
        connections from source to destination.

        Args:
            microgrid_id: Identifier of the microgrid to fetch and model.

        Returns:
            A directed graph containing component nodes and connection edges.
        """
        components = await self._client.list_microgrid_electrical_components(
            microgrid_id
        )
        connections = (
            await self._client.list_microgrid_electrical_component_connections(
                microgrid_id
            )
        )

        nx = _require_networkx()
        graph = nx.DiGraph()

        for component in components:
            graph.add_node(
                component.id,
                name=component.name or str(component.id),
                category=_format_category(component.category),
                orig_id=component.id,
            )

        for connection in connections:
            if connection is None:
                continue
            graph.add_edge(connection.source, connection.destination)

        return graph

    def compute_layout(self, graph: Any) -> dict[Any, tuple[float, float]]:
        """Compute a layered node layout with the root on the left.

        Selects a root node, groups nodes by shortest-path distance from the root, and
        assigns (x, y) coordinates such that layers are spaced along the x-axis.

        Args:
            graph: A graph-like object containing nodes and edges.

        Returns:
            A mapping from node identifiers to (x, y) coordinates.
        """
        if not graph.nodes:
            return {}

        root_node = self._select_root(graph)
        layered_nodes = self._group_by_level(graph, root_node)
        return self._build_positions(layered_nodes)

    def _select_root(self, graph: Any) -> Any:
        """Select a root node for layout.

        Prefers a node with no incoming edges and at least one outgoing edge. If no such
        node exists, falls back to an arbitrary node.

        Args:
            graph: A graph-like object containing nodes and edges.

        Returns:
            The selected root node identifier.
        """
        roots = [
            node
            for node in graph.nodes
            if graph.in_degree(node) == 0 and graph.out_degree(node) > 0
        ]
        return roots[0] if roots else list(graph.nodes)[0]

    def _group_by_level(self, graph: Any, root_node: Any) -> dict[int, list[Any]]:
        """Group nodes into layers by shortest-path distance from a root node.

        Nodes reachable from the root are assigned to layers based on their shortest-path
        distance. Nodes not reachable from the root are placed into a final "orphan"
        layer after the deepest reachable layer.

        Args:
            graph: A graph-like object containing nodes and edges.
            root_node: The node to treat as the root for distance computation.

        Returns:
            A mapping from layer index to the list of nodes in that layer.
        """
        nx = _require_networkx()
        levels = nx.single_source_shortest_path_length(graph, root_node)
        layered_nodes: dict[int, list[Any]] = {}
        for node, dist in levels.items():
            layered_nodes.setdefault(dist, []).append(node)

        orphans = [node for node in graph.nodes if node not in levels]
        if orphans:
            orphan_layer = max(layered_nodes.keys()) + 1 if layered_nodes else 0
            layered_nodes[orphan_layer] = orphans
        return layered_nodes

    def _build_positions(
        self, layered_nodes: dict[int, list[Any]]
    ) -> dict[Any, tuple[float, float]]:
        """Compute node positions from pre-grouped layers.

        Assigns x-coordinates based on layer index and y-coordinates by distributing
        nodes evenly within each layer.

        Args:
            layered_nodes: Mapping from layer index to the list of nodes in that layer.

        Returns:
            A mapping from node identifiers to (x, y) coordinates.
        """
        x_spacing, y_spacing = 2.5, 1.2
        pos: dict[Any, tuple[float, float]] = {}
        for level, nodes in layered_nodes.items():
            x_pos = level * x_spacing
            sorted_nodes = sorted(nodes, key=str)
            y_start = (len(sorted_nodes) - 1) * y_spacing / 2
            for i, node in enumerate(sorted_nodes):
                pos[node] = (x_pos, y_start - (i * y_spacing))
        return pos

    def render(
        self, graph: Any, pos: dict[Any, tuple[float, float]], options: RenderOptions
    ) -> None:
        """Render a component graph to an image file and optionally display it.

        This method uses NetworkX and Matplotlib to draw the given graph using the
        provided node positions, applies basic styling (labels, colors, arrows),
        saves the resulting figure to the path specified in ``options.output``,
        and, if configured, opens an interactive window to show the plot.

        Args:
            graph: A NetworkX graph-like object (typically a ``DiGraph``) whose
                nodes and edges represent the microgrid components and their
                electrical connections.
            pos: A mapping from node identifiers to ``(x, y)`` coordinates used
                to place each node in the rendered figure, usually obtained from
                :meth:`compute_layout`.
            options: Rendering configuration, including output file path, whether
                to show the figure interactively, figure size, and plot title.
        """
        nx = _require_networkx()
        plt = _require_matplotlib()

        node_labels = {
            node: (
                f'{graph.nodes[node].get("name", str(node))}\n'
                f'ID: {graph.nodes[node].get("orig_id", node)}'
            )
            for node in graph.nodes
        }

        plt.figure(figsize=options.figsize)
        nx.draw(
            graph,
            pos,
            with_labels=True,
            labels=node_labels,
            node_color="lightblue",
            edge_color="gray",
            node_size=800,
            font_size=8,
        )
        plt.title(options.title)
        plt.tight_layout()
        plt.savefig(options.output, dpi=300)
        if options.show:
            plt.show()
