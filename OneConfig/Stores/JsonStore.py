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
from ..Util import StrUtil
from ..Util.CaseInsensitiveDict import CaseInsensitiveDict
from .StoreResult import StoreResult


class JsonFileStore(IStore):
    _logger = logging.getLogger(__name__)

    @classmethod
    def from_json_params(cls, params: json):
        try:
            name = list(params.keys())[0] # the name of the params object is a name of the store
            path = FileUtil.expand_approot(params[name][Const.STORE_PATH_ATTR])
        except Exception as err:
            raise Errors.StoreInitError(f'Error opening config store with parameters passed. Check the origical exception below for more info') from err

        return JsonFileStore(name, path)


    def __init__(self, name: str, path: str):
        super().__init__()
        self._name = name
        self._path = path

        try: 
            with open(self._path) as f:
                self._store = json.load(f, object_pairs_hook=CaseInsensitiveDict) # case insensitive keys comparison in json
        except FileNotFoundError as err:
            raise Errors.StoreNotFound() from err
        except Exception as err:  
            raise Errors.StoreOpenError() from err
    
            
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
        if len(subkeys) > Const.KEY_MAX_LEVELS:
            raise Errors.KeyNestingLimit

        for subkey in subkeys:
            if len(subkey) == 0 or len(subkey) > Const.KEY_MAX_LEN:
                raise Errors.KeyProblem(f'Length of the subkey should be between 1 and {Const.KEY_MAX_LEN}', subkey, config_key)

        return subkeys

    def _process_lookup_excepion(self, subkey: str, key: str, ex: Exception) -> StoreResult:
        '''
        ### Processes exceptions in traversing keys
         - raises Errors.TraverseProblem in case IStore.raise_traverse_problems == True
         - returns default StoreResult otherwise
        '''
        if self.raise_traverse_problems:
            raise Errors.KeyProblem(subkey, key, self.name, ex)
        else:
            self._logger.warn(f'Subkey "{subkey}" of the key "{key}" is not found in the store "{self.name}", returning default value. Exception: {ex}')
            return StoreResult(None)

    # def _parse_value(self, )

    def _inner_get(self, key: str) -> StoreResult:
        # config_key, sensor_key = StrUtil.find_sensor_in_key(key)
        config_key = key

        # traverse through subkeys to the required level
        # as a result, curr_json will have the json object of desired hierarchy
        curr_json = self._store
        for subkey in self._split_config_key(config_key):
            try:
                curr_json = curr_json[subkey]
            except KeyError as ex: # Question: are there other types or ex possible? What to do with them?
                return self._process_lookup_excepion(subkey, key, ex)

        # process sensor key
        # if len(sensor_key) > 0:
        #     try:
        #         return StoreResult(curr_json[sensor_key])
        #     except KeyError as ex: # Question: are there other types or ex possible? What to do with them?
        #         try:
        #             return StoreResult(curr_json[Const.SENSOR_DEFAULT]) # try default sensor value
        #         except KeyError as ex:
        #             return self._process_lookup_excepion(sensor_key, key, ex)
        else:
            return StoreResult(curr_json)
