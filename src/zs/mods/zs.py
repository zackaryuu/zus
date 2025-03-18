import click
import os
from zs.common.zs import INSTALLED_PATH, isBuiltinPkg
from zs.mods import MOD_PATH

@click.group()
def cli():
    pass


@cli.command()
@click.option("--builtin", "-b", is_flag=True, help="List builtin packages")
@click.option("--installed", "-i", is_flag=True, help="List installed packages")
def list(builtin, installed):
    both = not builtin and not installed

    if builtin:
        if not both:
            click.echo("Builtin packages:")
        for pkg in os.listdir(MOD_PATH):
            if isBuiltinPkg(pkg):
                if not both:
                    click.echo(pkg)
                else:
                    click.echo(f"{pkg} (builtin)")

    if installed:
        if not both:
            click.echo("Installed packages:")
        for pkg in os.listdir(INSTALLED_PATH):
            if not both:
                click.echo(pkg)
            else:
                click.echo(f"{pkg} (installed)")

if __name__ == "__main__":
    cli()
