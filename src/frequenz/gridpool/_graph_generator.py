# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Formula generation from assets API component/connection configurations."""

import logging

from frequenz.client.assets import AssetsApiClient
from frequenz.client.assets.electrical_component import (
    Breaker,
    ComponentConnection,
    ElectricalComponent,
)
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId
from frequenz.microgrid_component_graph import ComponentGraph

_logger = logging.getLogger(__name__)


class ComponentGraphGenerator:
    """Generates component graphs for microgrids using the Assets API."""

    def __init__(
        self,
        client: AssetsApiClient,
    ) -> None:
        """Initialize this instance.

        Args:
            client: The Assets API client to use for fetching components and
                connections.
        """
        self._client: AssetsApiClient = client

    async def get_component_graph(
        self, microgrid_id: MicrogridId
    ) -> ComponentGraph[
        ElectricalComponent, ComponentConnection, ElectricalComponentId
    ]:
        """Generate a component graph for the given microgrid ID.

        Args:
            microgrid_id: The ID of the microgrid to generate the graph for.

        Returns:
            The component graph representing the microgrid's electrical
                components and their connections.

        Raises:
            ValueError: If any component connections could not be loaded.
        """
        components = await self._client.list_microgrid_electrical_components(
            microgrid_id
        )
        connections = (
            await self._client.list_microgrid_electrical_component_connections(
                microgrid_id
            )
        )

        if any(c is None for c in connections):
            raise ValueError("Failed to load all electrical component connections.")

        breakers = [c for c in components if isinstance(c, Breaker)]
        connected_breakers = [
            b
            for b in breakers
            if any(
                b.id in (c.source, c.destination) for c in connections if c is not None
            )
        ]

        if connected_breakers:
            _logger.warning(
                "The following breakers are connected to other components, "
                + "which is not supported by the component graph generator and may "
                + "lead to graph traversal issues: %s",
                [b.id for b in connected_breakers],
            )
        elif breakers:
            _logger.debug("Dropping unconnected breakers: %s", [b.id for b in breakers])
            components = [c for c in components if not isinstance(c, Breaker)]

        graph = ComponentGraph[
            ElectricalComponent, ComponentConnection, ElectricalComponentId
        ](components, connections)

        return graph
