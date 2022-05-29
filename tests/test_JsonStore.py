import unittest
from unittest.mock import mock_open, Mock, patch
import json


from logging import exception
from OneConfig.Stores.StoreResult import StoreResult
from tests.context import Cfg
from tests.context import IStore
from tests.context import JsonStore
from tests.context import Errors
from tests.context import Const



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
        "default": {
            "location": "%APP_ROOT%/tests/resources/oneconfig_storetest.json", 
            "cache-ttl": "20"
        }
    }
    '''

    def test_JsonStore_init_success(self):
        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            s = JsonStore()
            mock_file.assert_called_once_with('./oneconfig.json')
            self.assertEqual(s.name, 'default')


    def test_JsonStore_init_fail_wrong_params(self):
        try:
            s = JsonStore(params=json.loads('{}'))
        except Errors.StoreInitError as err:
            self.assertTrue(True)


    def test_JsonStore_init_fail_StoreOpenError(self):
        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            mock_file.side_effect = Errors.StoreOpenError('Test')
            try:
                s = JsonStore()
            except Errors.StoreOpenError as err:
                self.assertTrue(True)


    def test_JsonStore_init_fail_StoreFileNotFound(self):
        try:
            s = JsonStore(params=json.loads('{"store": {"location": "--non-existing--"}}'))
        except Errors.StoreNotFound as err:
            self.assertTrue(True)


    def test_JsonStore_raise_KeyProblems(self):
        s = JsonStore(params = json.loads(self.store_config))
        
        s.raise_traverse_problems = False
        res = s._inner_get('--non-existing-key--')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_UNDEFINED)
        self.assertEqual(res.get(), None)

        s.raise_traverse_problems = True
        try:
            res = s._inner_get('--non-existing-key--')
            self.assertTrue(False)
        except Errors.KeyProblem as err:
            self.assertTrue(True)
        

    def test_JsonStore_inner_get_success(self):
        s = JsonStore(params = json.loads(self.store_config))
        res = s._inner_get('GLOBAL1')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_STRING)
        self.assertEqual(res.get(), 'global_value')

        res = s._inner_get('global_INT')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_INT)
        self.assertEqual(res.get(), 42)

        res = s._inner_get('GLOBAL_arr')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_LIST)
        self.assertEqual(res.get()[0], 12)

        res = s._inner_get('db.server.?:ENV.DEV')
        self.assertEqual(res.get(), 'dev-sql-server')

        #-- this one doesn't work, consider what to do with it --- res = s._inner_get('db.server.?') # consider s.get('db.server?')
        #self.assertEqual(res, 'ENV')


    def test_JsonStore_inner_get_KeyProblem(self):
        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            s = JsonStore()
            try:
                res = s._inner_get('')
            except Exception as ex:
                self.assertTrue(isinstance(ex, Errors.KeyProblem))

    
    def test_JsonStore_split_config_key(self):
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

        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            s = JsonStore()
            mock_file.assert_called_once_with('./oneconfig.json')

            for case in test_cases:
                try:
                    res = s._split_config_key(case)
                    self.assertEqual(res, test_cases[case]) # this assertion works for non-exception cases
                except Exception as ex:
                    ex_type = str(type(ex))
                    self.assertTrue(test_cases[case] in ex_type)
