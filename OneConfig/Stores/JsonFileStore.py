# pylint: disable=invalid-name
import json
import logging
from typing import List

# pylint: disable=relative-beyond-top-level
from .. import Errors
from .. import Const
from ..IStore import IStore 
from ..Util import FileUtil
from ..Util.CaseInsensitiveDict import CaseInsensitiveDict
from ..StoreResult import StoreResult


class JsonFileStore(IStore):
    _logger = logging.getLogger(__name__)

    def __init__(self, name: str, content: str):
        super().__init__()
        self._name = name

        try: 
            self._store = json.loads(content, object_pairs_hook=CaseInsensitiveDict) # case insensitive keys comparison in json
        except Exception as err:  
            raise Errors.StoreOpenError() from err
    

    @classmethod
    def from_json_params(cls, store_name: str, params: json) -> 'JsonFileStore':
        try:
            path = FileUtil.expand_approot(params[Const.STORE_PATH_ATTR])
        except Exception as err:
            raise Errors.StoreInitError('Error opening config store with parameters passed. Check the origical exception below for more info') from err

        try: 
            with open(path, encoding="utf8") as f:
                raw_content = f.read() 
        except OSError as err:  
            raise Errors.StoreNotFound() from err


        return JsonFileStore(store_name, raw_content)


    @property
    def name(self):
        return self._name


    def get(self, key: str) -> StoreResult:
        config_key = key

        # traverse through subkeys to the required level
        # as a result, curr_json will have the json object of desired hierarchy
        curr_json = self._store
        for subkey in self._split_config_key(config_key):
            try:
                curr_json = curr_json[subkey]
            except KeyError as ex: # Question: are there other types or ex possible? What to do with them?
                return self._process_lookup_excepion(subkey, key, ex)
        return StoreResult(curr_json, self.allow_object_result)


    def _open_store(self, name: str):
        with open(name) as f:
            self._store = json.load(f)


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
        
        self._logger.warning(f'Subkey "{subkey}" of the key "{key}" is not found in the store "{self.name}", returning default value. Exception: {ex}')
        return StoreResult(None)
