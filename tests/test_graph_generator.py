# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the component graph generator."""

from unittest.mock import AsyncMock, MagicMock

from frequenz.client.assets import AssetsApiClient
from frequenz.client.assets.electrical_component import (
    ComponentConnection,
    GridConnectionPoint,
    Meter,
    SolarInverter,
)
from frequenz.client.common.microgrid import MicrogridId
from frequenz.client.common.microgrid.electrical_components import ElectricalComponentId

from frequenz.gridpool._graph_generator import ComponentGraphGenerator


async def test_formula_generation() -> None:
    """Test formula generation from component graph created from Assets API."""
    assets_client_mock = MagicMock(spec=AssetsApiClient)
    assets_client_mock.list_microgrid_electrical_components = AsyncMock(
        return_value=[
            GridConnectionPoint(
                id=ElectricalComponentId(1),
                microgrid_id=MicrogridId(10),
                rated_fuse_current=100,
            ),
            Meter(
                id=ElectricalComponentId(2),
                microgrid_id=MicrogridId(10),
            ),
            Meter(
                id=ElectricalComponentId(3),
                microgrid_id=MicrogridId(10),
            ),
            SolarInverter(
                id=ElectricalComponentId(4),
                microgrid_id=MicrogridId(10),
            ),
        ]
    )
    assets_client_mock.list_microgrid_electrical_component_connections = AsyncMock(
        return_value=[
            ComponentConnection(
                source=ElectricalComponentId(1),
                destination=ElectricalComponentId(2),
            ),
            ComponentConnection(
                source=ElectricalComponentId(1),
                destination=ElectricalComponentId(3),
            ),
            ComponentConnection(
                source=ElectricalComponentId(2),
                destination=ElectricalComponentId(4),
            ),
        ]
    )

    g = ComponentGraphGenerator(assets_client_mock)
    graph = await g.get_component_graph(MicrogridId(10))

    assert graph.grid_formula() == "COALESCE(#2, #4, 0.0) + #3"
    assert graph.pv_formula(None) == "COALESCE(#2, #4, 0.0)"
