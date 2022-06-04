import sys
import os
import glob
import logging

from pathlib import Path
from typing import List

from OneConfig.IStore import IStore
from OneConfig.Stores.JsonStore import JsonStore
from OneConfig import Errors
from OneConfig import Const


class Cfg:

    _stores = dict() # store_id -> IStore
    _configCache = dict() # key -> str
    _root_config_path = Path()
    _logger = logging.getLogger(__name__)

    def __init__(self, config_path = None, stores = None):
        print('Cfg init', self)
        if config_path:
            self._root_config_path = config_path
        else: # use app directory
            # https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
            self._root_config_path = self._get_config_root()

        self._default_store_path = self._find_default_store_path()
        # if not stores:
        #     aa = JsonStore('def-store')
        #     self.add_store(JsonStore('def-store'))


    def add_store(self, store: IStore) -> None:
        self._stores[store.name] = store

    def print_stores(self):
        for store in self._stores:
            print(f'{store} -> {self._stores[store]}')

    def get(self, key: str) -> str:
        if key.startswith('$'):
            store_name, target_key = key.split('.', 2)

    def _get_config_root(self) -> Path:
        return Path(getattr(sys, '_MEIPASS', Path.cwd()))

    def _find_default_store_path(self) -> str:
        paths = glob.glob('**/' + Const.STORE_NAME_TEMPLATE, root_dir=self._root_config_path, recursive=True)
        if len(paths) == 0:
            raise Errors.StoreNotFound(f'File with the name template "{Const.STORE_NAME_TEMPLATE}" cannot be found under the "{self._root_config_path}"')
        elif len(paths) > 1:
            self._logger.warning(f'More than one config store found under the root directory "{self._root_config_path}", the first found path will be used. List of found paths: "{paths}"')

        self._logger.info(f'Config store "{paths[0]}" will be opened as default OneConfig store')
        return paths[0]
