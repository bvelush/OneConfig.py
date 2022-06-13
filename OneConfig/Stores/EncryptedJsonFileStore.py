# pylint: disable=invalid-name
import json
import logging
from typing import List
from cryptography.fernet import Fernet

# pylint: disable=relative-beyond-top-level
from .. import Errors
from .. import Const
from ..IStore import IStore 
from ..Util import FileUtil
from ..Util.CaseInsensitiveDict import CaseInsensitiveDict
from ..Stores.JsonFileStore import JsonFileStore
from ..StoreResult import StoreResult


class EncryptedJsonFileStore(JsonFileStore):

    _logger = logging.getLogger(__name__)

    def __init__(self, name: str, content: str):
        super().__init__(name, content)
    

    @classmethod
    def from_json_params(cls, store_name: str, params: json) -> 'EncryptedJsonFileStore':
        try:
            path = FileUtil.expand_approot(params[Const.STORE_PATH_ATTR])
            keypath = FileUtil.expand_approot(params[Const.STORE_KEYPATH_ATTR])
        except Exception as err:
            raise Errors.StoreInitError('Error opening config store with parameters passed. Check the origical exception below for more info') from err


                # opening the key
        with open(keypath, 'rb') as keyfile:
            key = keyfile.read()

        # using the key
        fernet = Fernet(key)
        
        # opening the encrypted file
        with open(path, 'rb') as enc_file:
            encrypted = enc_file.read()
        
        # decrypting the file
        decrypted = fernet.decrypt(encrypted).decode()
        
        # opening the file in write mode and
        # writing the decrypted data

        return EncryptedJsonFileStore(store_name, decrypted)