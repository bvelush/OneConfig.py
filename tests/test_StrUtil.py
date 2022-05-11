# from ..OneConfig.Util import StrUtil
from context import StrUtil

import unittest

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
        for case in test_cases:
            self.assertEqual(StrUtil.split_key(case), test_cases[case])