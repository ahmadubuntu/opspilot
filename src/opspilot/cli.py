import typer

from opspilot.version import __version__


app = typer.Typer(
    help="OpsPilot CLI",
)


@app.command()
def version() -> None:
    """
    Show the current OpsPilot version.
    """

    typer.echo(__version__)


if __name__ == "__main__":
    app()
