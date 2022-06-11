# pylint: disable=invalid-name
# pylint: disable=logging-fstring-interpolation

import sys
import glob
import json
import logging

from typing import Dict
from pathlib import Path
from pydoc import locate

from OneConfig.IStore import IStore
from OneConfig.ISensor import ISensor
from OneConfig.StoreResult import StoreResult
from OneConfig import Errors
from OneConfig import Const
from OneConfig.Util.CaseInsensitiveDict import CaseInsensitiveDict


class Cfg:

    _stores: Dict[str, IStore] = CaseInsensitiveDict() # store_name -> IStore
    _sensors: Dict[str, ISensor] = CaseInsensitiveDict() # sensor_name -> ISensor
    _configCache: Dict[str, StoreResult] = CaseInsensitiveDict() # key -> StoreResult
    _root_config_path: Path = None
    _logger = logging.getLogger(__name__)

    def __init__(self):
        # region Open Default Store
        self._root_config_path = self._get_config_root()
        self._logger.info(f'OneConfig root directory detected: {self._root_config_path}')

        self._default_store_path = self._find_default_store_path(self._root_config_path)

        default_store_config_str = (Const.STORE_DEFAULT_CONFIG % str(self._default_store_path)) \
            .replace('\\', '\\\\')  # this is required on windows to make sure the path in JSON is in the right format
        
        default_store_config = json.loads(default_store_config_str)
        store = IStore.load_store_dynamically(Const.STORE_PREFIX, default_store_config) # name for default store is a store prefix
        store.raise_traverse_problems = False
        store.allow_object_result = True
        self.add_store(store)
        self._default_store = store
        # endregion Open Default Store

        # region Sensors init
        sensors_path = f'{Const.CFG_INIT_ATTR}.{Const.CFG_SENSORS_ATTR}'
        sensors_object = self._default_store.get(sensors_path)
        if sensors_object.type == StoreResult.ResultTypes.VAL_JSON_OBJECT:
            for sensor_name in sensors_object.value.keys():
                sensor_object = sensors_object.value[sensor_name]
                self.init_sensor(sensor_name, sensor_object)
        else:
            self._logger.warning(f'Sensors definition is not found in default configuration (path "{sensors_path}" is not present or is not valid sensor syntax')
        # endregion Sensors init

        # region Stores init
        stores_path = f'{Const.CFG_INIT_ATTR}.{Const.CFG_STORES_ATTR}'
        stores_object = self._default_store.get(stores_path)
        if stores_object.type == StoreResult.ResultTypes.VAL_JSON_OBJECT:
            for store_name in stores_object.value.keys():
                store_object = stores_object.value[store_name]
                self.init_store(store_name, store_object)
        else:
            self._logger.warning(f'Stores definition is not found in default configuration (path "{stores_path}" is not present or is not valid Stores syntax')

        # endregion Stores init
        store.allow_object_result = False

    

    def add_store(self, store: IStore) -> None:
        self._stores[store.name.upper()] = store

    def add_sensor(self, sensor: ISensor) -> None:
        self._sensors[sensor.name.upper()] = sensor

    def init_sensor(self, sensor_name: str, params: json) -> None:
        sensor = ISensor.load_sensor_dynamically(sensor_name, params)
        self.add_sensor(sensor)

    def init_store(self, store_name: str, params: json) -> None:
        store = IStore.load_store_dynamically(store_name, params)
        self.add_store(store)

    def print_stores(self):
        for store in self._stores:
            print(f'{store} -> {self._stores[store]}')

    def get(self, key: str) -> str:
        if key.startswith('$'):
            store_name, target_key = key.split('.', 2)

    def _get_config_root(self) -> Path:
        # https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
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
