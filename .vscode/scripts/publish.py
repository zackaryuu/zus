import os

if __name__ == "__main__":
    os.system("python .vscode/scripts/parseMods.py")
    os.system("python .vscode/scripts/gatherOnlineMods.py")

    # commit with messages
    commit_msg = input("Enter commit message: ")
    if not commit_msg:
        commit_msg = "misc: update index list"

    # add all changes
    os.system("git add .")
    os.system(f"git commit -m \"{commit_msg}\"")
    os.system("git push")