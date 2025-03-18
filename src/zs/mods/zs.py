import shutil
import click
import os
import json
import zs.common.zs as zs
import tempfile

PS2EXE_SCRIPT = """
#!/usr/bin/env pwsh
$cliPath = "{cli_path}"
python $cliPath @args
exit $LASTEXITCODE
"""

@click.group()
def cli():
    pass

@cli.command()
@click.argument("name")
@click.option("--giturl", "-g", help="Git URL")
def install(name : str, giturl : str):
    if giturl or name not in zs.listIndex():
        click.echo(f"zs.install: {name} not found")
        return

    if name in zs.listInstalled():
        click.echo(f"zs.install: {name} already installed")
        return
    
    if not giturl:
        giturl = f"https://github.com/zackaryuu/{name}.git"

    # git clone at INSTALLED_PATH
    os.system(f"git clone {giturl} {zs.INSTALLED_PATH}/{name}")

    cli_path = os.path.join(zs.INSTALLED_PATH, name, "cli.py")
    if not os.path.exists(cli_path):
        if os.path.exists(os.path.join(zs.INSTALLED_PATH, name, "src", "cli.py")):
            cli_path = os.path.join(zs.INSTALLED_PATH, name, "src", "cli.py")
        else:
            click.echo(f"zs.install: {name} not found")
            return

    # if no update
    if name in zs.listIndex() and zs.listIndex()[name]:
        # remove .git
        os.system(f"rm -rf {zs.INSTALLED_PATH}/{name}/.git")

    # create ps2exe script
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(PS2EXE_SCRIPT.format(cli_path=cli_path).encode())
        f.flush()
        os.system(f"ps2exe -inputFile {f.name} -outputFile {os.path.join(zs.SHIM_PATH, f'zs.{name}.exe')}")


@cli.command()
@click.argument("name", nargs=-1)
def update(name : list[str]):
    if not name:
        name = zs.listInstalled()

    for n in name:
        if n not in zs.listInstalled():
            click.echo(f"zs.update: {n} not installed")
            continue

        if not os.path.exists(os.path.join(zs.INSTALLED_PATH, n, ".git")):
            click.echo(f"zs.update: {n} not a git repository")
            continue

        # git pull
        os.system(f"git pull {zs.INSTALLED_PATH}/{n}")

@cli.command()
@click.argument("name", nargs=-1)
def remove(name : list[str]):
    if not name:
        click.echo("zs.remove: No name provided")
        return

    for n in name:
        if n not in zs.listInstalled():
            click.echo(f"zs.remove: {n} not installed")
            continue

        shutil.rmtree(os.path.join(zs.INSTALLED_PATH, n))

        os.remove(os.path.join(zs.SHIM_PATH, f"zs.{n}.exe"))

        click.echo(f"zs.remove: {n} removed")

@cli.group()
def list():
    pass

@list.command()
def builtin():
    for pkg in os.listdir(zs.MOD_PATH):
        if zs.isBuiltinPkg(pkg):
            pkg = pkg.replace(".py", "")
            click.echo(pkg)

@list.command()
def installed():
    for pkg in zs.listInstalled():
        click.echo(pkg)

@list.command()
def index():
    path = os.path.join(os.path.dirname(__file__), "orgRepos.json")
    with open(path, "r") as f:
        data = json.load(f)

    for pkg in data:
        if pkg in zs.listInstalled():
            click.echo(f"{pkg} (installed)")
        else:
            click.echo(pkg)

if __name__ == "__main__":
    cli()
