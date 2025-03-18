

import os
from zs.mods import MOD_PATH

def isBuiltinPkg(name : str)->bool:
    if not name.endswith(".py"):
        name = f"{name}.py"
    return os.path.exists(os.path.join(MOD_PATH, name))
    
INSTALLED_PATH = os.path.join(os.path.expanduser("~"), ".zs", "installed")

