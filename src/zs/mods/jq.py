from pprint import pformat
import click
import orjson
import os
import re
import subprocess

def save(file, data):
    with open(file, "wb", encoding="utf-8") as f:
        f.write(orjson.dumps(data))

@click.group(invoke_without_command=True, chain=True)
@click.argument("file", type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.pass_context
def cli(ctx, file):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

    ctx.ensure_object(dict)
    ctx.obj["file"] = orjson.loads(open(file, "rb").read())
    ctx.obj["path"] = file
    ctx.obj["args"] = {}

@cli.command(help="arg")
@click.argument("key", type=str)
@click.argument("value", type=str)
@click.pass_context
def arg(ctx, key, value):
    is_valid_path = value and os.path.exists(value)
    if is_valid_path:
        from zuu.util_file import load
        value = load(value)
    elif "@" in value:
        value = re.sub(r"@(\w+)", lambda m: ctx.obj["args"][m.group(1)], value)
        if value.startswith("["):
            # consider this a jq query by itself and execute it
            value = subprocess.check_output(["jq", value])
            value = orjson.loads(value)

    ctx.obj["args"][key] = value

@cli.command()
@click.pass_context
@click.argument("key", type=str)
def show(ctx, key):
    click.echo(pformat(ctx.obj["args"][key]))

@cli.command(help="jq patch")
@click.pass_context
def p(ctx):
    pass

@cli.result_callback()
def callback(ctx, result, **kwargs):
    save(ctx.obj["path"], ctx.obj["file"])

if __name__ == "__main__":
    cli()

