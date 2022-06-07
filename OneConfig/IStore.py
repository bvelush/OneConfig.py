import json
from pydoc import locate

from OneConfig import Errors
from OneConfig import Const

#from OneConfig.Stores.JsonFileStore import JsonFileStore
'''

'''

class IStore:
    '''
    '''

    def __init__(self):
        self._raise_traverse_problems = True

    @classmethod
    def from_json_params(cls, name: str, params: json):
        pass

    @classmethod
    def load_store_dynamically(cls, store_config: json):
        store_name = list(store_config.keys())[0]
        if not store_name.startswith(Const.STORE_PREFIX):
            raise Errors.StoreInitError(f'Store Name "{store_name} is expected to start with "{Const.STORE_PREFIX}"')
        
        store_type = store_config[store_name][Const.STORE_TYPE_ATTR]
        store_class = locate(store_type)
        if not issubclass(store_class, IStore):
            raise Errors.StoreInitError(f'Class "{store_class}" defined by "{Const.STORE_TYPE_ATTR}" in configuration, is expected to be an "IStore" instance ')
        store = store_class.from_json_params(store_name, store_config[store_name][Const.STORE_PARAMS_ATTR])
        return store

    def get(self, key: str) -> str:
        '''
        ***OVERRIDE IT***
        Returns the value of the key from the store.
        Can be hierarchical (via .) or flat. Hierarchy (if needed) must be implemented
        according to the logic of the store. For example, in the SQL store hierarchy could be
        table.key (always 2 levels), in JSON store -- just a path.to.the.value etc.
         '''
        pass

    @property
    def name(self) -> str:
        '''
        ***OVERRIDE IT***
        Returns the ID of the store
        '''
        pass

    @property
    def raise_traverse_problems(self) -> bool:
        return self._raise_traverse_problems

    @raise_traverse_problems.setter
    def raise_traverse_problems(self, val: bool):
        self._raise_traverse_problems = val
        