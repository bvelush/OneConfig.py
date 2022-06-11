# pylint: disable=invalid-name

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
        self.raise_traverse_problems = True
        self.allow_object_result = False

    @classmethod
    def from_json_params(cls, name: str, params: json) -> 'IStore':
        raise NotImplementedError('this method has to be overloaded in subclasses')

    @classmethod
    def load_store_dynamically(cls, store_name: str, store_config: json)-> 'IStore':
        if not store_name.startswith(Const.STORE_PREFIX):
            raise Errors.StoreInitError(f'Store Name "{store_name} is expected to start with "{Const.STORE_PREFIX}"')
        
        store_type = store_config[Const.STORE_TYPE_ATTR]
        store_class = locate(store_type)
        if not issubclass(store_class, IStore):
            raise Errors.StoreInitError(f'Class "{store_class}" defined by "{Const.STORE_TYPE_ATTR}" in configuration, is expected to be an "IStore" instance ')
        store = store_class.from_json_params(store_name, store_config[Const.STORE_PARAMS_ATTR])
        return store

    def get(self, key: str) -> str:
        '''
        ***OVERRIDE IT***
        Returns the value of the key from the store.
        Can be hierarchical (via .) or flat. Hierarchy (if needed) must be implemented
        according to the logic of the store. For example, in the SQL store hierarchy could be
        table.key (always 2 levels), in JSON store -- just a path.to.the.value etc.
         '''
        raise NotImplementedError('this method has to be overloaded in subclasses')

    @property
    def name(self) -> str:
        '''
        ***OVERRIDE IT***
        Returns the ID of the store
        '''
        raise NotImplementedError('this method has to be overloaded in subclasses')

    @property
    def raise_traverse_problems(self) -> bool:
        return self._raise_traverse_problems

    @raise_traverse_problems.setter
    def raise_traverse_problems(self, val: bool) -> None:
        self._raise_traverse_problems = val

    @property
    def allow_object_result(self) -> bool:
        return self._allow_object_result

    @allow_object_result.setter
    def allow_object_result(self, val: bool) -> None:
        self._allow_object_result = val
        