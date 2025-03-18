import click
import os
from zs import APP_CONFIG_PATH

def get_keyring(
    password : str | None = None
):
    try:
        from keyrings.cryptfile.cryptfile import CryptFileKeyring
    except ImportError:
        return click.echo("cryptfile is not installed, install with `pip install keyrings.cryptfile`")

    target_path = os.path.join(APP_CONFIG_PATH, "common", "crypt.store")
    keyring = CryptFileKeyring()
    keyring.file_path = target_path
    keyring.keyring_key = password
    lastmodified = os.path.getmtime(target_path)
    return keyring, lastmodified