import json

import unittest

from context import CaseInsensitiveDict

class Test_CaseInsensitiveDict(unittest.TestCase):

    js1 = '''
    {
        "key1": "val1", 
        "kEy2": {
            "keY3": "val3"
        }
    }
    '''

    def test_json(self):
        js = json.loads(self.js1, object_pairs_hook=CaseInsensitiveDict)
        self.assertEqual('val1', js['KEY1'])
        self.assertEqual('val3', js['key2']['key3'])
        