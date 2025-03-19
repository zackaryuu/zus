import shutil
import subprocess
import click
import os
import json
import zs.common.zs as zs
import tempfile
import toml

PS2EXE_SCRIPT = """
#!/usr/bin/env pwsh
$cliPath = "{cli_path}"
python $cliPath $args
exit $LASTEXITCODE
"""

BAT2EXE_SCRIPT = """
@echo off


if "%~1"=="--d" (
    set _tail=%*
    call set _tail=%%_tail:*%1=%%
    start /B python "{cli_path}" %_tail%
) else (
    python "{cli_path}" %*
)
exit /b %errorlevel%
"""


@click.group()
def cli():
    pass


@cli.command(help="Fill requirements")
@click.argument("pkg", nargs=-1)
def fillreq(pkg: list[str]):
    if not pkg:
        click.echo("zs.fillreq: No package provided")
        return

    for p in pkg:
        if p not in zs.listInstalled():
            click.echo(f"zs.fillreq: {p} not installed")
            continue

        req_path = os.path.join(zs.INSTALLED_PATH, p, "requirements.txt")
        if not os.path.exists(req_path):
            req_path = os.path.join(zs.INSTALLED_PATH, p, "pyproject.toml")

        if not os.path.exists(req_path):
            click.echo(f"zs.fillreq: {p} has no requirements")
            continue

        if req_path.endswith(".txt"):
            os.system(f"pip install -r {req_path}")
        elif req_path.endswith(".toml"):
            with open(req_path, "r") as f:
                data = toml.load(f)

            for dep in data["project"]["dependencies"]:
                os.system(f"pip install {dep}")

        click.echo(f"zs.fillreq: {p} filled")


@cli.command()
@click.argument("name")
@click.option("--giturl", "-g", help="Git URL")
@click.option("--local", "-l", type=click.Path(exists=True), help="Local path")
@click.option("--ps2exe", "-p", is_flag=True, help="Use ps2exe")
def install(name: str, giturl: str, local: str, ps2exe: bool):
    not_specified = not giturl and not local

    if not_specified and name not in zs.listIndex():
        click.echo(f"zs.install: {name} not found")
        return

    if name in zs.listInstalled():
        click.echo(f"zs.install: {name} already installed")
        return

    if not_specified:
        giturl = f"https://github.com/zackaryuu/{name}.git"

    if not local:
        # git clone at INSTALLED_PATH
        os.system(f"git clone {giturl} {zs.INSTALLED_PATH}/{name}")
    elif not zs.getCli(local):
        return click.echo(f"zs.install: cli for {name} not found")
    else:
        if os.path.exists(os.path.join(zs.INSTALLED_PATH, name)):
            shutil.rmtree(os.path.join(zs.INSTALLED_PATH, name))
        shutil.copytree(local, os.path.join(zs.INSTALLED_PATH, name))

    cli_path = zs.getCli(os.path.join(zs.INSTALLED_PATH, name))
    if not cli_path:
        click.echo(f"zs.install: {name} not found")
        return
    
    # if no update
    if name in zs.listIndex() and not zs.listIndex()[name]:
        click.echo(f"zs.install: removing {name} git given no future updates")
        shutil.rmtree(os.path.join(zs.INSTALLED_PATH, name, ".git"))

    # create SHIM
    try:
        temp_dir = None

        if not ps2exe:
            with open(os.path.join(zs.SHIM_PATH, f"zs.{name}.bat"), "w") as f:
                f.write(BAT2EXE_SCRIPT.format(cli_path=cli_path))
        elif shutil.which("ps2exe"):
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, "ps2exe.ps1")
            with open(temp_path, "w") as f:
                f.write(PS2EXE_SCRIPT.format(cli_path=cli_path))
            ps2exe_cmd = f"pwsh -c ps2exe -inputFile {temp_path} -outputFile {os.path.join(zs.SHIM_PATH, f'zs.{name}.exe')}"
            click.echo(ps2exe_cmd)
            os.system(ps2exe_cmd)
        else:
            click.echo("zs.install: ps2exe or bat2exe not found")
            return

    finally:
        if temp_dir:
            shutil.rmtree(temp_dir)

@cli.command()
@click.argument("name", nargs=-1)
@click.pass_context
def reset(ctx: click.Context, name: list[str]):
    if not name:
        name = [n for n in os.listdir(zs.INSTALLED_PATH) if os.path.isdir(os.path.join(zs.INSTALLED_PATH, n))]

    for pkg in name:
        # delete the shim target
        shim_path = os.path.join(zs.SHIM_PATH, f"zs.{pkg}.bat")
        if not os.path.exists(shim_path):
            for file in os.listdir(zs.SHIM_PATH):
                if file.startswith(f"zs.{pkg}"):
                    shim_path = os.path.join(zs.SHIM_PATH, file)
                    break

        if os.path.exists(shim_path):
            os.remove(shim_path)
    
        ctx.invoke(install, name=pkg)

    click.echo("zs.reset: all packages reset")
    

@cli.command()
@click.argument("name", nargs=-1)
def update(name: list[str]):
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
        subprocess.run(["git", "pull"], cwd=os.path.join(zs.INSTALLED_PATH, n))
        click.echo(f"zs.update: {n} updated")


@cli.command()
@click.argument("name", nargs=-1)
def remove(name: list[str]):
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
