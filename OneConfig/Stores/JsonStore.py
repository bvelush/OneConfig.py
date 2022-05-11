from ..IStore import IStore
from .. import Errors
from .. import Const
from .StoreResult import StoreResult
from ..Util import StrUtil

import json
import logging
from typing import List, Tuple

class JsonStore(IStore):
    logger = logging.getLogger(__name__)

    def __init__(self, name: str, store: json):
        self._name = name
        self._store = store
        self._exception_when_no_key = True

    @property
    def name(self):
        return self._name

    def get(self, key: str) -> str:
        return 'store-value'

    def _find_sensor_in_key(self, key: str) -> Tuple[str, str]:
        '''
        ### Separates the store key to the config and sensor parts
        In OneConfig, the full key consists of:
        - [optional] store_key: $store_key.
        - config_key: subkey1.subkey2
        - [optional] sensor_key: ?sensor_key

        ### input: config_key?sensor_key
        ### output: (config_key, sensor_key). Sensor key length will be 0 if sensor is not present
        Example:
        - for 'some.config.key?DEV' return will be ('some.config.key', 'DEV')
        - for 'some.other.key' will return ('some.other.key', '')
        '''
        sensor_position = key.find(Const.SENSOR_DELIMITER)
        sensor_present = sensor_position >= 0
        if sensor_present:
            return key[:sensor_position], key[sensor_position+1:]
        else:
            return key, ''

    def _split_config_key(self, config_key: str) -> List[str]:
        '''
        ### Splits composite config_key to subkeys and checks for their allowed limits
        Example:
        - 'subkey1.subkey2' -> ['subkey1', 'subkey2']
        '''
        subkeys = config_key.split('.')
        if len(subkeys) > Const.MAX_KEY_LEVELS:
            raise Errors.KeyNestingLimit

        for subkey in subkeys:
            if len(subkey) == 0 or len(subkey) > Const.MAX_SUBKEY_LEN:
                raise Errors.KeyProblem(f'Length of the subkey should be between 1 and {Const.MAX_SUBKEY_LEN}', subkey, config_key)

        return subkeys

    def _process_lookup_excepion(self, subkey: str, key: str, ex: Exception) -> StoreResult:
        '''
        ### Processes exceptions in traversing keys
         - raises Errors.TraverseProblem in case IStore.raise_traverse_problems == True
         - returns default StoreResult otherwise
        '''
        if self.raise_traverse_problems:
            raise Errors.TraverseProblem(subkey, key, self.name, ex)
        else:
            self.logger.warn(f'Subkey "{subkey}" of the key "{key}" is not found in the store "{self.name}", returning default value. Exception: {ex}')
            return StoreResult(None)

    def _inner_get(self, key: str) -> StoreResult:
        config_key, sensor_key = self._find_sensor_in_key(key)

        # traverse through subkeys to the required level
        # as a result, curr_json will have the json object of desired hierarchy
        curr_json = self._store
        for subkey in self._split_config_key(config_key):
            try:
                curr_json = curr_json[subkey]
            except KeyError as ex: # Question: are there other types or ex possible? What to do with them?
                return self._process_lookup_excepion(subkey, key, ex)

        # process sensor key
        if len(sensor_key) > 0:
            try:
                return StoreResult(curr_json[sensor_key])
            except KeyError as ex: # Question: are there other types or ex possible? What to do with them?
                try:
                    return StoreResult(curr_json[Const.SENSOR_DEFAULT]) # try default sensor value
                except KeyError as ex:
                    return self._process_lookup_excepion(sensor_key, key, ex)
        else:
            return StoreResult(curr_json)



