import json
from functools import cache
import os
from zs.mods import MOD_PATH

SHIM_PATH = os.path.join(os.path.expanduser("~"), ".zs", "shims")
INSTALLED_PATH = os.path.join(os.path.expanduser("~"), ".zs", "installed")

os.makedirs(INSTALLED_PATH, exist_ok=True)
os.makedirs(SHIM_PATH, exist_ok=True)


def isBuiltinPkg(name: str) -> bool:
    if not name.endswith(".py"):
        name = f"{name}.py"
    return os.path.exists(os.path.join(MOD_PATH, name))


@cache
def listInstalled() -> list[str]:
    installed = []
    for pkg in os.listdir(SHIM_PATH):
        if pkg.startswith(".") or pkg.startswith("_"):
            continue

        pkg = os.path.splitext(pkg)[0]
        pkg = pkg.replace("zs.", "")
        installed.append(pkg)
    return installed


@cache
def listIndex() -> dict[str, bool]:
    with open(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mods", "orgRepos.json"
        ),
        "r",
    ) as f:
        data = json.load(f)

    return data


def getCli(path: str) -> str:
    cli_path = os.path.join(path, "cli.py")
    if os.path.exists(cli_path):
        pass
    elif os.path.exists(os.path.join(path, "src", "cli.py")):
        cli_path = os.path.join(path, "src", "cli.py")
    elif os.path.exists(os.path.join(path, "src")):
        folders = os.listdir(os.path.join(path, "src"))
        folders = [f for f in folders if not f.startswith(".") or not f.startswith("_")]
        if len(folders) == 1:
            cli_path = os.path.join(path, "src", folders[0], "cli.py")
    else:
        return None
    return cli_path
