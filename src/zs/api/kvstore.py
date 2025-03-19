import re
import os
import json
from zs import APP_CONFIG_PATH

FOLDER_PATH = os.path.join(APP_CONFIG_PATH, "kvstore")
PATH = os.path.join(FOLDER_PATH, "index.json")
if not os.path.exists(PATH):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)


class KVStore:
    with open(PATH, "r", encoding="utf-8") as f:
        INDEX = json.load(f)

    @staticmethod
    def load():
        with open(PATH, "r", encoding="utf-8") as f:
            KVStore.INDEX = json.load(f)

    @staticmethod
    def save():
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump(KVStore.INDEX, f, ensure_ascii=False, indent=4)

    @staticmethod
    def get(key: str):
        return KVStore.INDEX.get(key)

    @staticmethod
    def set(key: str, value: str, no_existing: bool = False):
        if no_existing and key in KVStore.INDEX:
            return False
        KVStore.INDEX[key] = value
        KVStore.save()
        return True

    @staticmethod
    def delete(key: str):
        if key not in KVStore.INDEX:
            return
        del KVStore.INDEX[key]
        KVStore.save()

    @staticmethod
    def clear():
        KVStore.INDEX.clear()
        KVStore.save()


def parse_document(document: str):
    pattern = r"<\$@(\w+)>"
    matches = re.findall(pattern, document)

    for match in matches:
        key = match
        snippet = KVStore.get(key)

        if snippet is None:
            raise ValueError(f"Key {key} not found in store")
        document = re.sub(
            r"^//<\$@" + re.escape(key) + ">",
            f"<$@{key}>",
            document,
            flags=re.MULTILINE,
        )
        document = re.sub(
            r"^#<\$@" + re.escape(key) + ">", f"<$@{key}>", document, flags=re.MULTILINE
        )
        document = document.replace(f"<$@{key}>", snippet)

    return document
