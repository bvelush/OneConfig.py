# pylint: disable=invalid-name
# pylint: disable=logging-fstring-interpolation

import sys
import glob
import json
import logging
import re
import os

from typing import Dict, Any
from pathlib import Path

from OneConfig.IStore import IStore
from OneConfig.ISensor import ISensor
from OneConfig.StoreResult import StoreResult
from OneConfig import Errors
from OneConfig import Const
from OneConfig.Util.CaseInsensitiveDict import CaseInsensitiveDict
from OneConfig.Util import FileUtil


class Cfg:

    _stores: Dict[str, IStore] = CaseInsensitiveDict() # store_name -> IStore
    _sensors: Dict[str, ISensor] = CaseInsensitiveDict() # sensor_name -> ISensor
    _configCache: Dict[str, StoreResult] = CaseInsensitiveDict() # key -> StoreResult
    _root_config_path: Path = None
    _logger = logging.getLogger(__name__)
    _STR_CONFIGKEY = r'(?P<fullKey>((?P<store>\$[\w\-]*)\.)?(?P<path>[\w\-]+(\.[\w\-\?\:]+)*)+)'
    _RX_STR_CONFIGKEY = re.compile(_STR_CONFIGKEY)
    _RX_STR_INLINE_CONFIGKEY = re.compile(r'(\{\{\{){1}' + _STR_CONFIGKEY + r'(\}\}\}){1}')

    def __init__(self, default_store_path: str=None) -> None:
        # region Open Default Store
        if default_store_path:
            default_store_path = FileUtil.expand_approot(default_store_path)
            if Path(default_store_path).is_dir():
                self._root_config_path = Path(default_store_path)
                self._default_store_path = self._find_default_store_path(self._root_config_path)
            else:
                self._root_config_path = os.path.dirname(default_store_path)
                self._default_store_path = default_store_path
        else:
            self._root_config_path = self._get_config_root()
            self._default_store_path = self._find_default_store_path(self._root_config_path)

        self._logger.info(f'OneConfig root directory detected: {self._root_config_path}')

        default_store_config_str = (Const.STORE_DEFAULT_CONFIG % str(self._default_store_path)) \
            .replace('\\', '\\\\')  # this is required on windows to make sure the path in JSON is in the right format
        
        default_store_config = json.loads(default_store_config_str)
        store = IStore.load_store_dynamically(Const.STORE_PREFIX, default_store_config) # name for default store is a store prefix
        store.raise_traverse_problems = False
        store.allow_object_result = True
        self._add_store(store)
        self._default_store = store
        # endregion Open Default Store

        # region Sensors init
        sensors_path = f'{Const.CFG_INIT_ATTR}.{Const.CFG_SENSORS_ATTR}'
        sensors_object = self._default_store.get(sensors_path)
        if sensors_object.type == StoreResult.ResultTypes.VAL_JSON_OBJECT:
            for sensor_name in sensors_object.value.keys():
                sensor_object = sensors_object.value[sensor_name]
                self._init_sensor(sensor_name, sensor_object)
        else:
            self._logger.warning(f'Sensors definition is not found in default configuration (path "{sensors_path}" is not present or is not valid sensor syntax')
        # endregion Sensors init

        # region Stores init
        stores_path = f'{Const.CFG_INIT_ATTR}.{Const.CFG_STORES_ATTR}'
        stores_object = self._default_store.get(stores_path)
        if stores_object.type == StoreResult.ResultTypes.VAL_JSON_OBJECT:
            for store_name in stores_object.value.keys():
                store_object = stores_object.value[store_name]
                self._init_store(store_name, store_object)
        else:
            self._logger.warning(f'Stores definition is not found in default configuration (path "{stores_path}" is not present or is not valid Stores syntax')

        # endregion Stores init
        store.allow_object_result = False


    def get(self, key: str) -> Any:
        try:
            return self._inner_get(key, 0)
        except Errors.KeyNestingLimit as err:
            msg = f'Keys and sensors nesting in the key "{key}" reached it\'s limit of "{Const.CFG_MAX_RECURSION}"'
            self._logger.error(msg)
            raise Errors.KeyNestingLimit(msg) from err


    def _inner_get(self, key: str, count: int) -> Any:  
        self._logger.debug(f'key:"{key}", count: "{count}"')
        if count > Const.CFG_MAX_RECURSION:
            raise Errors.KeyNestingLimit('TODO: Need traverse history')

        key_components = self._RX_STR_CONFIGKEY.search(key).groupdict()
        store = self._get_store(key_components['store'])
        result = store.get(key_components['path'])
        if result.is_bool or result.is_int or result.is_list:
            return result.value

        elif result.is_string: # the string could contain inner OneConfig keys, need to recursively resolve them
            value_to_return = result.value
            while True:
                inner_key = self._RX_STR_INLINE_CONFIGKEY.search(value_to_return)

                if inner_key:
                    # replace inner_key with inner_key_value in result.value:
                    inner_key_value = self._inner_get(inner_key.groupdict()['fullKey'], count+1)
                    if not isinstance(inner_key_value, str):
                        inner_key_value = str(inner_key_value)
                    value_to_return = self._RX_STR_INLINE_CONFIGKEY.sub(inner_key_value, value_to_return, count=1)
                else:
                    return value_to_return
                
        elif result.is_sensor:
            sensor_name = result.value[Const.SENSOR_RESULT_NAME]
            possible_sensor_options = result.value[Const.SENSOR_RESULT_KEYS]
            sensor = self._get_sensor(sensor_name)
            sensor_value = sensor.get()
            if sensor_value in possible_sensor_options:
                return self._inner_get(f'{key}.{sensor_name}.{sensor_value}', count+1)
            
            self._logger.warning(f'returned sensor value "{sensor_value}" for sensor "{sensor_name}" in key "{key}" is not one of possible options. Trying DEFAULT')
            return self._inner_get(f'{key}.{sensor_name}.DEFAULT', count+1)

        elif result.is_object_keys: # TODO: ATTENTION! definition of is_undefined is JSON_OBJECT or UNDEFINED
            raise Errors.KeyProblem(f'key: "{key}", count: "{count}", components: "{key_components}", result: "{result.value}"')
        else:
            raise Errors.KeyProblem(f'key: "{key}", count: "{count}", components: "{key_components}", result: "{result.value}"')

    def _get_store(self, store_name: str) -> IStore:
        if not store_name:
            store_name = Const.STORE_PREFIX
        return self._stores[store_name]

    def _get_sensor(self, sensor_name: str) -> ISensor:
        return self._sensors[sensor_name]

    def _add_store(self, store: IStore) -> None:
        self._stores[store.name.upper()] = store

    def _add_sensor(self, sensor: ISensor) -> None:
        self._sensors[sensor.name.upper()] = sensor

    def _init_sensor(self, sensor_name: str, params: json) -> None:
        sensor = ISensor.load_sensor_dynamically(sensor_name, params)
        self._add_sensor(sensor)

    def _init_store(self, store_name: str, params: json) -> None:
        store = IStore.load_store_dynamically(store_name, params)
        self._add_store(store)

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
