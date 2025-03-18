
import os
import click
import subprocess

from zs.api.diffStore import DiffStore

@click.command()
@click.option("--password", "-p", help="Password for the keyring")
@click.option("--version", "-v", help="Select the default match")
@click.option("--push", "-P", is_flag=True, help="Record current entry too")
@click.option("--open-datafolder", is_flag=True, help="Open the data folder")
@click.argument("command", nargs=-1)
def cli(password, command, version, push, open_datafolder):
    if not command:
        click.echo("zs.diff: No command provided")
        return

    if password == "$":
        password = click.prompt("Password", hide_input=True)
    elif password.startswith("env:"):
        password = os.environ[password[4:]]
    elif password.startswith("file:"):
        with open(password[5:], "r") as f:
            password = f.read()
    elif password.startswith("keyring:"):
        from zuu.etc import os_keyring
        password = os_keyring.get_password(password[8:])

    if not version:
        version = "latest"
    
    DiffStore.init(password)
    command = " ".join(command)
    click.echo(f"zs.diff: Running {command}")
    try:
        # Join command tuple into string and use shell=True to resolve executable path
        run_result = subprocess.run(command, shell=True, capture_output=True, text=True)
    except FileNotFoundError as e:
        click.echo(f"zs.diff: Command not found - {e}")
        return
    
    if run_result.returncode != 0:
        click.echo("zs.diff: Command failed")
        click.echo(run_result.stderr)
        return
    
    # No need to decode since we're using text=True
    result = run_result.stdout.strip()

    if DiffStore.lastmodified:
        click.echo(f"zs.diff: Last modified: {DiffStore.lastmodified}")
    
    data = DiffStore._get_diffItem(command)

    if push:
        DiffStore.set(command, result)

    click.echo(f"zs.diff: Result\n=======\n{result}\n=======")

    if open_datafolder and DiffStore.lastmodified:
        os.startfile(os.path.dirname(DiffStore.keyringItem.file_path))
        return

    if not data:
        click.echo("zs.diff: No past entry")
        return
    
    verf = DiffStore.get(command, version, data)
    if verf == result:
        click.echo(f"zs.diff: Verfied {version}")
        return
    
    click.echo("zs.diff: Failed")
    
    
    



if __name__ == "__main__":
    cli()