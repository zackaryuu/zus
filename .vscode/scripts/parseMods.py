import os
import toml

if __name__ == "__main__":
    mods_dir = os.path.join("src", "zs", "mods")
    projects_toml = toml.load("pyproject.toml")

    scripts = {}

    for mod in os.listdir(mods_dir):
        if mod.startswith("_"):
            continue
        modname = mod.replace(".py", "")
        scripts[f"zs.{modname}" if modname != "zs" else "zs"] = f"zs.mods.{modname}:cli"

    projects_toml["project"]["scripts"] = scripts

    with open("pyproject.toml", "w") as f:
        toml.dump(projects_toml, f)
