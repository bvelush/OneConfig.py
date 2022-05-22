# pylint: disable=invalid-name

import unittest
from context import StrUtil

class TestCfg(unittest.TestCase):

    def test_splitkey(self):
        test_cases = {
            'key': ('key', ''),
            'k1.k2': ('k1', 'k2'),
            'k1.k2.k3': ('k1', 'k2.k3'),
            '.k2': ('', 'k2'),
            'k1.': ('k1', ''),
            '.': ('', ''),
            '': ('',''),
            '..': ('', '.')
        }
        for case, case_result in test_cases.items():
            self.assertEqual(StrUtil.split_key(case), case_result)

    def test_JsonStore_find_sensor_in_key(self):
        test_cases = {
            'some.config.key?DEV': ('some.config.key', 'DEV'),
            'some.config.key': ('some.config.key', ''),
            '?DEV': ('', 'DEV'),
            '': ('', ''),
            'some.config.key?': ('some.config.key', ''),
        }
        for case, case_result in test_cases.items():
            res = StrUtil.find_sensor_in_key(case)
            self.assertEqual(res, case_result)