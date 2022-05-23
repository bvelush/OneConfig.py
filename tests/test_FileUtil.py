# pylint: disable=invalid-name

import unittest
from unittest.mock import patch
from context import FileUtil
from context import Const


class Test_FileUtil(unittest.TestCase):

    def test_expand_approot(self):
        suffix = '/config/app.cfg.init'
        mock_replace = 'aaa'

        orig_str = Const.STORE_APPROOT_TEMPLATE + suffix
        with patch('OneConfig.Util.FileUtil.Path.cwd', lambda: mock_replace) as m:
            ret_val = FileUtil.expand_approot(orig_str)
            self.assertEqual(mock_replace + suffix, ret_val)
            
