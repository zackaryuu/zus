import json
import hashlib
import os
import typing

class DiffStore:
    keyringItem = None
    lastmodified = None
    
    DiffItem = typing.Dict[int, typing.Union[int, str]]

    @staticmethod
    def init(
        password : str | None = None
    ):
        from zs.common.cryptfile import get_keyring
        DiffStore.keyringItem, DiffStore.lastmodified = get_keyring(password)

    @staticmethod
    def _get_diffItem(
        key : str
    ) -> DiffItem | None:
        if not DiffStore.keyringItem:
            raise Exception("DiffStore not initialized")
        
        if not DiffStore.lastmodified:
            data = DiffStore.keyringItem.get_password("zs.diffstore", "zs")
            if not data:
                return None
            
            data2 = json.loads(data)
            del data

            return data2.get(key, None)
        
        key = f"DiffStore:{hashlib.md5(key.encode()).hexdigest()}"
        val = DiffStore.keyringItem.get_password("zs",key)
        if not val:
            return None
        
        return json.loads(val)

    @staticmethod
    def _condense(data):
        # condense the data to save space
        versionsDict = {}
        refDict = {}
        for i in range(len(data)):
            val = data[i]
            if val in refDict:
                versionsDict[i] = refDict[val]
            else:
                versionsDict[i] = val
                refDict[val] = i


    @staticmethod
    def _set_diffItem(
        key : str,
        data : DiffItem
    ):
        if not DiffStore.keyringItem:
            raise Exception("DiffStore not initialized")

        # storage logic    
        if not DiffStore.lastmodified:
            host = DiffStore.keyringItem.get_password("zs.diffstore", "zs")
            if not host:
                host = {}
            else:
                host = json.loads(host)

            host[key] = data
            DiffStore.keyringItem.set_password("zs.diffstore", "zs", json.dumps(host))
        else:
            key = f"DiffStore:{hashlib.md5(key.encode()).hexdigest()}"
            DiffStore.keyringItem.set_password("zs", key, json.dumps(data))
            DiffStore.lastmodified = os.path.getmtime(DiffStore.keyringItem.file_path)        
        
    @staticmethod
    def _get(
        key : str,
        data,
        version : str = "latest",
    ):
        assert version in ["latest", "previous"] or version.isdigit()
        
        if version == "latest":
            return data[str(len(data) - 1)]

        if version == "previous":
            return data[str(len(data) - 2)]

        return data[version]

    @staticmethod
    def get(
        key : str,
        version : str = "latest",
        _data : DiffItem | None = None
    ) -> str | None:
        if _data:
            data = _data
        else:
            data = DiffStore._get_diffItem(key)
            if not data:
                return None

        got = DiffStore._get(key, data, version)
        
        if isinstance(got, int):
            return data[str(got)]
        else:
            return got

    @staticmethod
    def set(
        key : str,
        val : str
    ):
        data = DiffStore._get_diffItem(key)
        if not data:
            data : DiffStore.DiffItem = {0 : val}
        else:
            if val in data.values():
                index = list(data.values()).index(val)
                data[len(data)] = index
            else:
                data[len(data)] = val
    
        DiffStore._set_diffItem(key, data)

        

