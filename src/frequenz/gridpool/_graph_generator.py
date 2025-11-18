# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Formula generation from assets API component/connection configurations."""

from typing import cast

from frequenz.client.assets import AssetsApiClient
from frequenz.client.assets.electrical_component import (
    ComponentConnection,
    ElectricalComponent,
)
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId
from frequenz.microgrid_component_graph import ComponentGraph


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

        graph = ComponentGraph[
            ElectricalComponent, ComponentConnection, ElectricalComponentId
        ](components, cast(list[ComponentConnection], connections))

        return graph
