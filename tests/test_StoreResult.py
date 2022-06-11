# pylint: disable=invalid-name

import json
import unittest

from context import StoreResult

class Test_StoreResult(unittest.TestCase):

    json_types = json.loads('''
        {
            "integer": 42, 
            "real": 4.2,
            "string": "some string", 
            "boolean": true, 
            "list": [1, "item2", false],
            "object": {
                "key1": "field1",
                "key2": {
                    "sub_object": [1, 2, 3]
                },
                "key3": [4, "5", 6]
            },
            "sensor": {
                "?:sensor_name": {
                    "sensor_key1": "value1",
                    "sensor_key2": "value2",
                    "sensor_key3": "value3"
                }
            }
        }
    ''')

    def test_StoreResult_int(self):
        sr = StoreResult(self.json_types['integer'])
        self.assertEqual(sr.type, StoreResult.ResultTypes.VAL_INT)
        self.assertEqual(sr.value, 42)
        self.assertTrue(sr.is_int)
        self.assertFalse(sr.is_undefined)
        self.assertFalse(sr.is_bool)
        self.assertFalse(sr.is_string)
        self.assertFalse(sr.is_list)
        self.assertFalse(sr.is_object)
        self.assertFalse(sr.is_sensor)

    def test_StoreResult_real_undefined(self):
        sr = StoreResult(self.json_types['real'])
        # real/float type is not implemented currently
        self.assertEqual(sr.type, StoreResult.ResultTypes.VAL_UNDEFINED)
        self.assertEqual(sr.value, 4.2)  
        self.assertTrue(sr.is_undefined)
        self.assertFalse(sr.is_int)
        self.assertFalse(sr.is_bool)
        self.assertFalse(sr.is_string)
        self.assertFalse(sr.is_list)
        self.assertFalse(sr.is_object)
        self.assertFalse(sr.is_sensor)

    def test_StoreResult_string(self):
        sr = StoreResult(self.json_types['string'])
        self.assertEqual(sr.type, StoreResult.ResultTypes.VAL_STRING)
        self.assertEqual(sr.value, 'some string')
        self.assertTrue(sr.is_string)
        self.assertFalse(sr.is_undefined)
        self.assertFalse(sr.is_int)
        self.assertFalse(sr.is_bool)
        self.assertFalse(sr.is_list)
        self.assertFalse(sr.is_object)
        self.assertFalse(sr.is_sensor)        

    def test_StoreResult_boolean(self):
        sr = StoreResult(self.json_types['boolean'])
        self.assertEqual(sr.type, StoreResult.ResultTypes.VAL_BOOL)
        self.assertEqual(sr.value, True)
        self.assertTrue(sr.is_bool)
        self.assertFalse(sr.is_undefined)
        self.assertFalse(sr.is_int)
        self.assertFalse(sr.is_string)
        self.assertFalse(sr.is_list)
        self.assertFalse(sr.is_object)
        self.assertFalse(sr.is_sensor)        

    def test_StoreResult_list(self):
        sr = StoreResult(self.json_types['list'])
        self.assertEqual(sr.type, StoreResult.ResultTypes.VAL_LIST)
        self.assertSequenceEqual(sr.value, [1, 'item2', False])
        self.assertTrue(sr.is_list)
        self.assertFalse(sr.is_undefined)
        self.assertFalse(sr.is_int)
        self.assertFalse(sr.is_bool)
        self.assertFalse(sr.is_string)
        self.assertFalse(sr.is_object)
        self.assertFalse(sr.is_sensor)        

    def test_StoreResult_object_keys(self):
        sr = StoreResult(self.json_types['object'])
        self.assertEqual(sr.type, StoreResult.ResultTypes.VAL_OBJECT_KEYS)
        self.assertSequenceEqual(sr.value, ['KEY1', 'KEY2', 'KEY3']) # note the capitalization
        self.assertTrue(sr.is_object)
        self.assertFalse(sr.is_undefined)
        self.assertFalse(sr.is_int)
        self.assertFalse(sr.is_bool)
        self.assertFalse(sr.is_string)
        self.assertFalse(sr.is_list)
        self.assertFalse(sr.is_sensor) 

    def test_StoreResult_json_object(self):
        sr = StoreResult(self.json_types['object'], allow_objects=True)
        self.assertEqual(sr.type, StoreResult.ResultTypes.VAL_JSON_OBJECT)
        self.assertEqual(sr.value, self.json_types['object'])
        self.assertFalse(sr.is_object)
        self.assertFalse(sr.is_undefined)
        self.assertFalse(sr.is_int)
        self.assertFalse(sr.is_bool)
        self.assertFalse(sr.is_string)
        self.assertFalse(sr.is_list)
        self.assertFalse(sr.is_sensor) 