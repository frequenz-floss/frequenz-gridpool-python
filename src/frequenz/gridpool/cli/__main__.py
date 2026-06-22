# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CLI tool for gridpool functionality."""

import os
from pathlib import Path

import asyncclick as click
from frequenz.client.assets import AssetsApiClient
from frequenz.client.common.microgrid import MicrogridId

from frequenz.gridpool import ComponentGraphGenerator, load_configs
from frequenz.gridpool.cli._dump_config import dump_map
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


@cli.command("generate-config")
@click.argument("microgrid_ids", type=int, nargs=-1)
@click.option(
    "--default",
    "default_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Config file whose values the Assets API overrides (lowest precedence).",
)
@click.option(
    "--override",
    "override_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Config file whose values override the Assets API (highest precedence).",
)
async def generate_config(
    microgrid_ids: tuple[int, ...],
    default_file: Path | None,
    override_file: Path | None,
) -> None:
    """Generate microgrid config from the Assets API as TOML.

    Derives metadata, formulas and component IDs for the given microgrid IDs and
    prints the result as dotted-key TOML to stdout.

    `--default` and `--override` each take a config file and are layered with the
    Assets API by precedence: `--default` < Assets API < `--override`. So a file
    passed as `--override` keeps its values where it has them (the API only fills
    gaps), while a file passed as `--default` is overridden by the API. If no
    microgrid IDs are given, they are taken from the supplied files. Files are
    only read; redirect stdout to save the result.
    """
    url = os.environ.get("ASSETS_API_URL")
    key = os.environ.get("ASSETS_API_AUTH_KEY")
    secret = os.environ.get("ASSETS_API_SIGN_SECRET")
    if not url or not key or not secret:
        raise click.ClickException(
            "ASSETS_API_URL, ASSETS_API_AUTH_KEY, ASSETS_API_SIGN_SECRET must be set."
        )

    async with AssetsApiClient(url, auth_key=key, sign_secret=secret) as client:
        configs = await load_configs(
            default_files=default_file,
            assets_client=client,
            override_files=override_file,
            microgrid_ids=list(dict.fromkeys(microgrid_ids)) or None,
        )

    if not configs:
        raise click.ClickException("No microgrids could be loaded; nothing to write.")

    click.echo(dump_map(configs), nl=False)


def main() -> None:
    """Run the CLI tool."""
    cli(_anyio_backend="asyncio")


if __name__ == "__main__":
    main()
