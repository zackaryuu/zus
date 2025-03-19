from hashlib import sha256
import click
import os
import importlib


@click.command()
@click.argument("path", type=str)
def cli(path):
    if not os.path.exists(path):
        package = importlib.import_module(path)
        # get package path
        try:
            file = getattr(package, "__file__", None)
            if not file:
                package_path = os.path.dirname(package.__path__)[0]
            else:
                package_path = os.path.dirname(file)
        except:  # noqa
            click.echo(f"Error getting package path for {path}")
            return
    else:
        package_path = path

    hd = sha256()

    for root, dirs, files in os.walk(package_path):
        if "__pycache__" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "rb") as f:
                    while True:
                        chunk = f.read(4096)  # Read in 4KB chunks
                        if not chunk:  # End of file
                            break
                        hd.update(chunk)  # Update hash with chunk

    click.echo(hd.hexdigest())


if __name__ == "__main__":
    cli()
