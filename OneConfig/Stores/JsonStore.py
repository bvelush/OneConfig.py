# pylint: disable=invalid-name
import json
import logging
import glob
from typing import List, Tuple

# pylint: disable=relative-beyond-top-level
from .. import Errors
from .. import Const
from ..IStore import IStore 
from ..ISensor import ISensor
from ..Util import FileUtil
from .StoreResult import StoreResult


class JsonStore(IStore):
    logger = logging.getLogger(__name__)

    def __init__(self, name: str, sensors: List[ISensor]=None, params: json=None):
        self._name = name
        self._sensors = sensors
        self._params = params
        self._exception_when_no_key = True

        try:
            self._location = self._params[Const.STORE_LOCATION_ATTR]
        except Exception as err:
            raise Errors.StoreNotFound('Attribute "location" is not found in store parameters') from err

        self._location = FileUtil.expand_approot(self._location)
        


    @property
    def name(self):
        return self._name

    def _open_store(self, name: str):

        aa  = FileUtil.get_app_path()

        with open(name) as f:
            self._store = json.load(f)

    def get(self, key: str) -> str:
        return 'store-value'

    
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



