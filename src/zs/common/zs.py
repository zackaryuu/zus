import json
from functools import cache
import os
from zs.mods import MOD_PATH

SHIM_PATH = os.path.join(os.path.expanduser("~"), ".zs", "shims")
INSTALLED_PATH = os.path.join(os.path.expanduser("~"), ".zs", "installed")

os.makedirs(INSTALLED_PATH, exist_ok=True)
os.makedirs(SHIM_PATH, exist_ok=True)

def isBuiltinPkg(name : str)->bool:
    if not name.endswith(".py"):
        name = f"{name}.py"
    return os.path.exists(os.path.join(MOD_PATH, name))
    

@cache
def listInstalled()->list[str]:
    installed = []
    for pkg in os.listdir(SHIM_PATH):
        if pkg.startswith(".") or pkg.startswith("_"):
            continue

        pkg = pkg.replace(".exe", "")
        pkg = pkg.replace("zs", "")
        installed.append(pkg)
    return installed

@cache
def listIndex()-> dict[str, bool]:
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "mods", "orgRepos.json"), "r") as f:
        data = json.load(f)

    return data