# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CLI tool for gridpool functionality."""

import os

import asyncclick as click
from frequenz.client.assets import AssetsApiClient
from frequenz.client.common.microgrid import MicrogridId

from frequenz.gridpool import ComponentGraphGenerator
from frequenz.gridpool.cli._render_graph import ComponentGraphRenderer, RenderOptions


@click.group()
async def cli() -> None:
    """CLI tool for gridpool functionality."""


@cli.command()
@click.argument("microgrid_id", type=int)
@click.option(
    "--prefix",
    type=str,
    default="{component}",
    help="Prefix format for the output (Supports {microgrid_id} and {component} placeholders).",
)
async def print_formulas(
    microgrid_id: int,
    prefix: str,
) -> None:
    """Fetch and print component graph formulas for a microgrid."""
    url = os.environ.get("ASSETS_API_URL")
    key = os.environ.get("ASSETS_API_AUTH_KEY")
    secret = os.environ.get("ASSETS_API_SIGN_SECRET")
    if not url or not key or not secret:
        raise click.ClickException(
            "ASSETS_API_URL, ASSETS_API_AUTH_KEY, ASSETS_API_SIGN_SECRET must be set."
        )

    async with AssetsApiClient(
        url,
        auth_key=key,
        sign_secret=secret,
    ) as client:
        cgg = ComponentGraphGenerator(client)

        graph = await cgg.get_component_graph(MicrogridId(microgrid_id))
        power_formulas = {
            "consumption": graph.consumer_formula(),
            "generation": graph.producer_formula(),
            "grid": graph.grid_formula(),
            "pv": graph.pv_formula(None),
            "battery": graph.battery_formula(None),
            "chp": graph.chp_formula(None),
            "ev": graph.ev_charger_formula(None),
        }

        for component, formula in power_formulas.items():
            print(
                prefix.format(component=component, microgrid_id=microgrid_id)
                + f' = "{formula}"'
            )


@cli.command("render-graph")
@click.argument("microgrid_id", type=int)
@click.option(
    "--output",
    type=click.Path(dir_okay=False, writable=True),
    default="component_graph.png",
    show_default=True,
    help="Output image path.",
)
@click.option(
    "--show/--no-show",
    default=True,
    show_default=True,
    help="Display the graph interactively.",
)
async def render_graph(microgrid_id: int, output: str, show: bool) -> None:
    """Render and save a component graph visualization for a microgrid."""
    url = os.environ.get("ASSETS_API_URL")
    key = os.environ.get("ASSETS_API_AUTH_KEY")
    secret = os.environ.get("ASSETS_API_SIGN_SECRET")
    if not url or not key or not secret:
        raise click.ClickException(
            "ASSETS_API_URL, ASSETS_API_AUTH_KEY, ASSETS_API_SIGN_SECRET must be set."
        )

    try:
        async with AssetsApiClient(
            url,
            auth_key=key,
            sign_secret=secret,
        ) as client:
            renderer = ComponentGraphRenderer(client)
            graph = await renderer.build_graph(MicrogridId(microgrid_id))
            if not graph.nodes:
                raise click.ClickException("No components found for this microgrid.")
            pos = renderer.compute_layout(graph)
            renderer.render(graph, pos, RenderOptions(output=output, show=show))
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc


def main() -> None:
    """Run the CLI tool."""
    cli(_anyio_backend="asyncio")


if __name__ == "__main__":
    main()
