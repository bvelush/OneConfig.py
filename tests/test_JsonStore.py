import unittest
from unittest.mock import mock_open, Mock, patch
import json

from logging import exception
from context import StoreResult
from context import Cfg
from context import IStore
from context import JsonFileStore
from context import Errors
from context import Const


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
            "path": "%APP_ROOT%/tests/resources/oneconfig_storetest.json"
        }
    }
    '''

    js_with_init_stores = '''
        {
            "OneConfig": {
                "stores": {
                    "$SEC": {
                        "type": "OneConfig.Stores.JsonFileStore", 
                        "path": "%APP_ROOT%/tests/resources/testJsonFileStore.cfg.json"
                    },
                    "$INI": {
                        "type": "OneConfig.Stores.IniFileStore",
                        "path": "%APP_ROOT%/tests/resources/oneconfig_storetest.json",
                        "params": {
                            "k1": "v1",
                            "k2": "v2"
                        }
                    }                    
                },
                "sensors": {
                    "env": {
                        "type": "OneConfig.Sensors.EnvSensor",
                        "arg1": "somestring",
                        "arg2": 42
                    }
                }
            }
        }
    '''

    def test_JsonStore_init_success(self):
        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            s = JsonFileStore('default', 'path')
            mock_file.assert_called_once_with('path')
            self.assertEqual(s.name, 'default')

    def test_JsonStore_init_fail_wrong_params(self):
        try:
            s = JsonFileStore.from_json_params(params=json.loads('{}'))
        except Errors.StoreInitError as err:
            self.assertTrue(True)

    def test_JsonStore_init_fail_StoreOpenError(self):
        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            mock_file.side_effect = Errors.StoreOpenError('Test')
            try:
                s = JsonFileStore('name', 'path')
                self.assertTrue(False) # should not go here
            except Errors.StoreOpenError as err:
                self.assertTrue(True)

    def test_JsonStore_init_fail_StoreInitError(self):
        try:
            s = JsonFileStore.from_json_params(params=json.loads('{"store_name": {"no-path": "--doesnt matter--"}}')) # required parameter 'path' is not in params
            self.assertTrue(False) # should not go here
        except Errors.StoreInitError as err:
            self.assertTrue(True)

    def test_JsonStore_init_fail_StoreFileNotFound(self):
        try:
            s = JsonFileStore.from_json_params(params=json.loads('{"store_name": {"path": "--non-existing--"}}'))
        except Errors.StoreNotFound as err:
            self.assertTrue(True)

    def test_JsonStore_raise_KeyProblems(self):
        s = JsonFileStore.from_json_params(params = json.loads(self.store_config))
        
        s.raise_traverse_problems = False
        res = s._inner_get('--non-existing-key--')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_UNDEFINED)
        self.assertEqual(res.value, None)

        s.raise_traverse_problems = True
        try:
            res = s._inner_get('--non-existing-key--')
            self.assertTrue(False)
        except Errors.KeyProblem as err:
            self.assertTrue(True)
        
    def test_JsonStore_inner_get_StoreResult(self):
        s = JsonFileStore.from_json_params(params = json.loads(self.store_config))

        res = s._inner_get('db.server')
        self.assertEqual(res.value[Const.SENSOR_RESULT_NAME], 'ENV')
        self.assertSequenceEqual(res.value[Const.SENSOR_RESULT_KEYS], ['DEV', 'TEST'])

        res = s._inner_get('GLOBAL1')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_STRING)
        self.assertEqual(res.value, 'global_value')

        res = s._inner_get('global_INT')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_INT)
        self.assertEqual(res.value, 42)

        res = s._inner_get('GLOBAL_arr')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_LIST)
        self.assertEqual(res.value[0], 12)

        res = s._inner_get('db.server.?:ENV.DEV')
        self.assertEqual(res.value, 'dev-sql-server')

    def test_JsonStore_inner_get_KeyProblem(self):
        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            s = JsonFileStore('name', 'path')
            try:
                res = s._inner_get('')
            except Exception as ex:
                self.assertTrue(isinstance(ex, Errors.KeyProblem))
    
    def test_JsonStore_split_config_key(self):
        test_cases = {
            '': 'KeyProblem',  # empty keys not allowed
            's1.s': ['s1', 's'],
            's1': ['s1'],
            's1.s2': ['s1', 's2'],
            's1.s2.s3.s4.s5.s6.s7.s8.s9.s10.s11.s12.s13.s14.s15': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14', 's15'],
            's1.s2.s3.s4.s5.s6.s7.s8.s9.s10.s11.s12.s13.s14.s15.s16': 'KeyNestingLimit', # too much nesting
            's1.s0123456789012345678901234567890.s3': ['s1', 's0123456789012345678901234567890', 's3'],
            's1.s01234567890123456789012345678901.s3': 'KeyProblem' # one of subkeys is over the length limit
        }

        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            s = JsonFileStore('name', 'path')
            mock_file.assert_called_once_with('path')

            for case in test_cases:
                try:
                    res = s._split_config_key(case)
                    self.assertEqual(res, test_cases[case]) # this assertion works for non-exception cases
                except Exception as ex:
                    ex_type = str(type(ex))
                    self.assertTrue(test_cases[case] in ex_type)

    def test_JsonStore_return_object_keys(self):
        with patch('OneConfig.Stores.JsonStore.open', mock_open(read_data=self.js_with_init_stores), create=True) as mock_file:
            s = JsonFileStore('default', 'path')

            res = s._inner_get(Const.CFG_INIT_ATTR)
            self.assertEqual(res.type, StoreResult.ResultTypes.VAL_OBJECT_KEYS)
            self.assertIn(Const.CFG_STORES_ATTR, res.value)
            self.assertIn(Const.CFG_SENSORS_ATTR, res.value)
