import sys
from pathlib import Path
from typing import List
from OneConfig.IStore import IStore
from OneConfig.Stores.JsonStore import JsonStore
from OneConfig.Errors import *

import os

class Cfg:


    _stores = dict() # store_id -> IStore
    _configCache = dict() # key -> str

    def __init__(self, config_path = None, stores = None):
        print('Cfg init', self)
        if config_path:
            self._config_path = config_path
        else: # use app directory
            # https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
            self._config_path = Path(getattr(sys, '_MEIPASS', Path.cwd()))
        if not stores:
            aa = JsonStore('def-store')
            self.add_store(JsonStore('def-store'))


    def add_store(self, store: IStore) -> None:
        self._stores[store.name] = store

    def print_stores(self):
        for store in self._stores:
            print(f'{store} -> {self._stores[store]}')

    def get(self, key: str) -> str:
        if key.startswith('$'):
            store_name, target_key = key.split('.', 2)

    def get_config_root(self) -> str:
        return
