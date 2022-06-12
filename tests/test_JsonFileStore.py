import unittest
from unittest.mock import mock_open, patch
import json

from context import StoreResult
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
        "path": "%APP_ROOT%/tests/resources/oneconfig_storetest.json"
    }
    '''

    js_with_init_stores = '''
        {
            "OneConfig": {
                "stores": {
                    "$SEC": {
                        "type": "OneConfig.Stores.JsonFileStore", 
                        "params": {
                            "path": "%APP_ROOT%/tests/resources/testJsonFileStore.cfg.json"
                        }
                    },
                    "$INI": {
                        "type": "OneConfig.Stores.IniFileStore",
                        "params": {
                            "path": "%APP_ROOT%/tests/resources/oneconfig_storetest.json",
                            "k1": "v1",
                            "k2": "v2"
                        }
                    }, 
                    "$DB": {
                        "type": "OneConfig.Stores.MySQLStore", 
                        "cache": "60",
                        "params": {
                            "server": "server1", 
                            "user": "user1",
                            "pw": "pw1"
                        }
                    }                    
                },
                "sensors": {
                    "?:Stage": {
                        "type": "OneConfig.Sensors.StageSensor",
                        "params": {
                            "arg1": "somestring",
                            "arg2": 42
                        }
                    },
                    "?:test_sensor": {
                        "type": "OneConfig.Sensors.EnvSensor",
                        "params": {
                            "envvar": "path"
                        }
                    }
                }
            }
        }
    '''

    def test_JsonStore_init_success(self):
        with patch('OneConfig.Stores.JsonFileStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            store = JsonFileStore('default', 'path')
            mock_file.assert_called_once_with('path')
            self.assertEqual(store.name, 'default')

    def test_JsonStore_init_fail_wrong_params(self):
        try:
            JsonFileStore.from_json_params('', params=json.loads('{}'))
            self.assertTrue(False)  # should not go here
        except Errors.StoreInitError:
            pass

    def test_JsonStore_init_fail_StoreOpenError(self):
        with patch('OneConfig.Stores.JsonFileStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            mock_file.side_effect = Errors.StoreOpenError('Test')
            try:
                JsonFileStore('name', 'path')
                self.assertTrue(False)  # should not go here
            except Errors.StoreOpenError:
                pass

    def test_JsonStore_init_fail_StoreInitError(self):
        try:
            JsonFileStore.from_json_params('store_name', params=json.loads('{"no-path": "--doesnt matter--"}')) # required parameter 'path' is not in params
            self.assertTrue(False)  # should not go here
        except Errors.StoreInitError:
            pass

    def test_JsonStore_init_fail_StoreFileNotFound(self):
        try:
            JsonFileStore.from_json_params('store_name', params=json.loads('{"path": "--non-existing--"}'))
            self.assertTrue(False)  # should not go here
        except Errors.StoreNotFound:
            pass

    def test_JsonStore_raise_KeyProblems(self):
        store = JsonFileStore.from_json_params('default', params = json.loads(self.store_config))
        
        store.raise_traverse_problems = False
        res = store.get('--non-existing-key--')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_UNDEFINED)
        self.assertEqual(res.value, None)

        store.raise_traverse_problems = True
        try:
            store.get('--non-existing-key--')
            self.assertTrue(False)  # should not go here
        except Errors.KeyProblem:
            pass
        
    def test_JsonStore_inner_get_StoreResult(self):
        store = JsonFileStore.from_json_params('$SEC', params = json.loads(self.store_config))

        res = store.get('db.server')
        self.assertEqual(res.value[Const.SENSOR_RESULT_NAME], '?:ENV')
        self.assertSequenceEqual(res.value[Const.SENSOR_RESULT_KEYS], ['DEV', 'TEST'])

        res = store.get('GLOBAL1')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_STRING)
        self.assertEqual(res.value, 'global_value')

        res = store.get('global_INT')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_INT)
        self.assertEqual(res.value, 42)

        res = store.get('GLOBAL_arr')
        self.assertEqual(res.type, StoreResult.ResultTypes.VAL_LIST)
        self.assertEqual(res.value[0], 12)

        res = store.get('db.server.?:ENV.DEV')
        self.assertEqual(res.value, 'dev-sql-server')

    def test_JsonStore_inner_get_KeyProblem(self):
        with patch('OneConfig.Stores.JsonFileStore.open', mock_open(read_data=self.js1), create=True):
            store = JsonFileStore('name', 'path')
            try:
                store.get('')
                self.assertTrue(False)  # should not go here
            except Exception as err:
                self.assertTrue(isinstance(err, Errors.KeyProblem))
    
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

        with patch('OneConfig.Stores.JsonFileStore.open', mock_open(read_data=self.js1), create=True) as mock_file:
            store = JsonFileStore('name', 'path')
            mock_file.assert_called_once_with('path')

            for case in test_cases:
                try:
                    res = store._split_config_key(case)
                    self.assertEqual(res, test_cases[case]) # this assertion works for non-exception cases
                except Exception as ex:
                    ex_type = str(type(ex))
                    self.assertTrue(test_cases[case] in ex_type)

    def test_JsonStore_return_object_keys(self):
        with patch('OneConfig.Stores.JsonFileStore.open', mock_open(read_data=self.js_with_init_stores), create=True) as mock_file:
            store = JsonFileStore('default', 'path')

            res = store.get(Const.CFG_INIT_ATTR)
            self.assertEqual(res.type, StoreResult.ResultTypes.VAL_OBJECT_KEYS)
            self.assertIn(Const.CFG_STORES_ATTR, res.value)
            self.assertIn(Const.CFG_SENSORS_ATTR, res.value)
