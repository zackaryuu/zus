
import json
import click
from zs.api.kvstore import KVStore, FOLDER_PATH
import os

@click.group()
def cli():
    pass

@cli.command()
@click.argument("key", type=str)
@click.option("-c", "--clipboard", is_flag=True)
def get(key, clipboard):
    if key not in KVStore.INDEX:
        click.echo(f"Key {key} not found")
        return
    if clipboard:
        from tkinter import Tk
        Tk().clipboard_set(KVStore.get(key))
        click.echo(f"Copied {key} to clipboard")
    else:
        click.echo(KVStore.get(key))

@cli.command(help="Sets the given key to the given value")
@click.argument("key", type=str)
@click.argument("value", type=str, required=False)
@click.option("-ne", "--no-existing", is_flag=True, help="check if the key exists")
def set(key, value, no_existing):
    if value is None:
        from tkinter import Tk
        value = Tk().clipboard_get()
    if KVStore.set(key, value, no_existing):
        click.echo(f"Set {key} to {value}")
    else:
        click.echo(f"Key {key} already exists")

@cli.command(help="Exports the current KVStore to a file")
@click.argument("file", type=click.Path())
def export(file):
    with open(file, "w") as f:
        json.dump(KVStore.INDEX, f)
    click.echo("KVStore exported")

@cli.command(help="Takes the given key and writes it to the given file")
@click.argument("key", type=str)
@click.argument("file", type=click.Path())
@click.option("-a", "--append", is_flag=True)
def touch(key, file, append):
    mode = "a" if append else "w"
    with open(file, mode, encoding="utf-8") as f:
        f.write(KVStore.get(key))
    click.echo(f"KVStore touched {key} to {file}")

@cli.command(help="Lists all keys")
def keys():
    for key in KVStore.INDEX.keys():
        click.echo(key)

@cli.command(help="Deletes the given key")
@click.argument("key", type=str)
def delete(key):
    KVStore.delete(key)
    click.echo(f"Deleted {key}")

@cli.command(help="Lists all keys that start with the given string")
@click.option("-s", "--start", type=str, default="" , help="Starts with this string")
def list(start):
    for key in KVStore.INDEX.keys():
        if key.startswith(start):
            click.echo(key)

@cli.command(help="Mirrors the current KVStore to a backup file")
def mirror():
    import shutil
    if os.path.exists(os.path.join(FOLDER_PATH, "index.json.backup")):
        os.remove(os.path.join(FOLDER_PATH, "index.json.backup"))
    shutil.copy(os.path.join(FOLDER_PATH, "index.json"), os.path.join(FOLDER_PATH, "index.json.backup"))
    KVStore.save()
    click.echo("KVStore mirrored")

@cli.command(help="Swaps the current and backup KVStore")
def swap():
    if os.path.exists(os.path.join(FOLDER_PATH, "index.json.backup")):
        os.rename(os.path.join(FOLDER_PATH, "index.json"), os.path.join(FOLDER_PATH, "index.json.backup2"))
        os.rename(os.path.join(FOLDER_PATH, "index.json.backup"), os.path.join(FOLDER_PATH, "index.json"))
        os.rename(os.path.join(FOLDER_PATH, "index.json.backup2"), os.path.join(FOLDER_PATH, "index.json.backup"))
        KVStore.load()
        click.echo("KVStore swapped")
    else:
        click.echo("No backup found")

@cli.command(help="Rename key")
@click.argument("old_key", type=str)
@click.argument("new_key", type=str)
def rename(old_key, new_key):
    if old_key not in KVStore.INDEX:
        click.echo(f"Key {old_key} not found")
        return
    if new_key in KVStore.INDEX:
        click.echo(f"Key {new_key} already exists")
        return
    old_value = KVStore.get(old_key)
    KVStore.delete(old_key)
    KVStore.set(new_key, old_value)
    click.echo(f"Renamed {old_key} to {new_key}")

@cli.command()
@click.argument("key", type=str)
@click.option("-c", "--coder", is_flag=True)
@click.option("-s", "--simple", is_flag=True)
def edit(key, coder, simple):
    if key not in KVStore.INDEX:
        click.echo(f"Key {key} not found")
        return
    # get current contents
    content = KVStore.get(key)
    
    # dump to a file
    with open(os.path.join(FOLDER_PATH, key), "w", encoding="utf-8") as f:
        f.write(content)
    # open in notepad
    if coder:
        os.system(f"code {os.path.join(FOLDER_PATH, key)}")
        print(f"Opened {os.path.join(FOLDER_PATH, key)} in VS Code")
    elif simple:
        # if windows
        if os.name == "nt": 
            os.system(f"notepad {os.path.join(FOLDER_PATH, key)}")
            print(f"Opened {os.path.join(FOLDER_PATH, key)} in Notepad")
        # if linux
        elif os.name == "posix":
            os.system(f"gedit {os.path.join(FOLDER_PATH, key)}")
            print(f"Opened {os.path.join(FOLDER_PATH, key)} in Gedit")
        # if mac
        elif os.name == "mac":
            os.system(f"open {os.path.join(FOLDER_PATH, key)}")
            print(f"Opened {os.path.join(FOLDER_PATH, key)} in TextEdit")

        else:
            raise Exception("Unsupported OS")
        
    else:
        os.startfile(os.path.join(FOLDER_PATH, key))
        print(f"Opened {os.path.join(FOLDER_PATH, key)}")
        input("Press Enter to Save...")
    
    # save the file content back to index
    with open(os.path.join(FOLDER_PATH, key), "r", encoding="utf-8") as f:
        KVStore.set(key, f.read())
    click.echo(f"Saved {os.path.join(FOLDER_PATH, key)}")

if __name__ == "__main__":
    cli()

