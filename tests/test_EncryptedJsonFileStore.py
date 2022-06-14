import unittest
from unittest.mock import mock_open, patch
import json

from context import StoreResult
from context import EncryptedJsonFileStore
from context import Errors
from context import Const


class TestEncryptedJsonStore(unittest.TestCase):
    params = '''
        {
            "path": "%APP_ROOT%/tests/resources/testJsonFileStore.cfg.bin", 
            "keypath": "c:/temp/keyfile.dev.bin"
        }
    '''

    def test_aa(self):
        store = EncryptedJsonFileStore.from_json_params('$sec', json.loads(self.params))
    