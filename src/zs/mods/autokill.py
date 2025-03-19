from zuu.util_procLifetime import lifetime, cleanup
import click
import subprocess


def run_cmd(cmd: str):
    subprocess.run(cmd, shell=True)


@click.command()
@click.argument("time", type=str)
@click.option("-p", "--process", type=str, help="Process name to kill", multiple=True)
@click.option("-w", "--window", type=str, help="Window name to kill", multiple=True)
@click.argument("cmd", nargs=-1, required=True)
def cli(time, cmd, process, window):
    try:
        import pygetwindow

    except ImportError:
        click.echo("pygetwindow is not installed")
        return

    try:
        import psutil
    except ImportError:
        click.echo("psutil is not installed")
        return

    func = lifetime(time)(run_cmd)
    func = cleanup(
        windows=window if window else True,
        processes=process if process else True,
        new_only=True,
    )(func)

    func(cmd)


if __name__ == "__main__":
    cli()
