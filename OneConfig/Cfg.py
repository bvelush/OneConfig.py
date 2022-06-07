# pylint: disable=invalid-name
# pylint: disable=logging-fstring-interpolation

from ast import Is
import sys
import glob
import json
import logging

from pathlib import Path
from pydoc import locate

from OneConfig.IStore import IStore
from OneConfig import Errors
from OneConfig import Const


class Cfg:

    _stores = {} # store_id -> IStore
    _configCache = {} # key -> str
    _root_config_path = Path()
    _logger = logging.getLogger(__name__)

    def __init__(self):
        # https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
        self._root_config_path = self._get_config_root()
        self._logger.info(f'OneConfig root directory detected: {self._root_config_path}')

        self._default_store_path = self._find_default_store_path(self._root_config_path)

        default_store_config_str = (Const.STORE_DEFAULT_CONFIG % str(self._default_store_path)) \
            .replace('\\', '\\\\')  # this is required on windows to make sure the path in JSON is in the right format
        
        default_store_config = json.loads(default_store_config_str)
        store = IStore.load_store_dynamically(default_store_config)
        self.add_store(store)
        print(self._default_store_path)
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

    def _find_default_store_path(self, root_path: Path) -> Path:
        paths = glob.glob('**/' + Const.STORE_NAME_TEMPLATE, root_dir=root_path, recursive=True)
        if len(paths) == 0:
            raise Errors.StoreNotFound(f'File with the name template "{Const.STORE_NAME_TEMPLATE}" cannot be found under the "{root_path}"')
        
        if len(paths) > 1:
            self._logger.warning(f'More than one config store found under the root directory "{root_path}", the first found path will be used. List of found paths: "{paths}"')

        store_path = Path.joinpath(root_path, paths[0])
        self._logger.info(f'Config store "{store_path}" will be opened as default OneConfig store')
        return store_path
