from logging import exception
from OneConfig.Stores.StoreResult import StoreResult
from tests.context import Cfg
from tests.context import IStore
from tests.context import JsonStore
from tests.context import Errors
from tests.context import Const

import json

import unittest
from unittest.mock import mock_open
from unittest.mock import patch

class TestJsonStore(unittest.TestCase):

    js1 = '''
        {
            "simple_key": "val1",
            "2-level-key": {
                "simple_key": "val2"
            },
            "simple_sensor": {
                "?": "TEST_SENSOR",
                "S1": "V1",
                "S2": "V2",
                "DEFAULT": "DV"
            }
        }
    '''

    store_config = '''
    {
        "location": "%APP_ROOT%/Stores/oneconfig.json", 
        "cache-ttl": "20"
    }
    '''

    def test_IStoreJsonTest(self):
        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            s = JsonStore('aa')
            s._open_store('aa.cfg')

            mock_file.assert_called_once_with('aa.cfg')

    def test_JsonStoreKvargs(self):
        s = JsonStore(Const.STORE_DEFAULT_NAME, sensors = None, params = json.loads(self.store_config))

    def test_aa(self):
        s = JsonStore('s1', json.loads(self.js1))

        res = s._inner_get('k2l1.k1l2')

        try:
            res = s._inner_get('')
        except Exception as ex:
            self.assertTrue(isinstance(ex, Errors.KeyProblem))

        res = s._inner_get('k')

    

    def test_JsonStore_split_config_key(self):
        s = JsonStore('s1', json.loads(self.js1))

        test_cases = {
            '': 'KeyProblem',
            's1.s': ['s1', 's'],
            's1': ['s1'],
            's1.s2': ['s1', 's2'],
            's1.s2.s3.s4.s5.s6.s7.s8.s9.s10.s11.s12.s13.s14.s15': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14', 's15'],
            's1.s2.s3.s4.s5.s6.s7.s8.s9.s10.s11.s12.s13.s14.s15.s16': 'KeyNestingLimit', # exception case
            's1.s01234567890123456789012345678901.s3': ['s1', 's01234567890123456789012345678901', 's3'],
            's1.s01234567890123456789012345678901.s3': 'KeyProblem' # exception case
        }

        for case in test_cases:
            try:
                res = s._split_config_key(case)
                self.assertEqual(res, test_cases[case]) # this assertion works for non-exception cases
            except Exception as ex:
                ex_type = str(type(ex))
                self.assertTrue(test_cases[case] in ex_type)

    def test_JsonStore_process_lookup_exception(self):
        s = JsonStore('s1', json.loads(self.js1))
        s.raise_traverse_problems = True
        try:
            s._process_lookup_excepion('', '', Exception())
            self.assertTrue(False) # we should not be here
        except Exception as ex:
            self.assertTrue(isinstance(ex, Errors.TraverseProblem))

        s.raise_traverse_problems = False
        res = s._process_lookup_excepion('', '', Exception())
        self.assertTrue(isinstance(res, StoreResult))

    def test_JsonStore_inner_get(self):
        s = JsonStore('s1', json.loads(self.js1))

        test_cases = {
            '': 'KeyProblem',
            'n': 'TraverseProblem',
            'simple_key': "val1"
        }

    # def test_JsonStore_ExceptionProp(self):
    #     s = JsonStore('s1', json.loads(self.js1))
    #     self.assertTrue(s.exception_when_no_key)

    #     s.exception_when_no_key = False
    #     self.assertFalse(s.exception_when_no_key)

    #     s.exception_when_no_key = True
    #     self.assertTrue(s.exception_when_no_key)


    # def test_JsonStore_inner_get_exception_when_not_ready(self):
    #     s = JsonStore('s1', json.loads(self.js1))

    #     # try with exception
    #     try:
    #         res = s._inner_get(None, 'aaa', 'aaa', [])
    #     except Exception as ex:
    #         self.assertTrue(isinstance(ex, Errors.ErrorConfigLookup))

    #     s.exception_when_no_key = False # disable exceptions
    #     res = s._inner_get(None, 'aaa', 'aaa', [])
    #     self.assertEqual(res, StoreResult.DEFAULT)

    # def test_JsonStore_inner_get_MAX_KEY_LEVELS(self):
    #     s = JsonStore('s1', json.loads(self.js1))
    #     try:
    #         res = s._inner_get()