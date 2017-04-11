import unittest
from misc.which import which
from misc.shell import shell


class WhichTest(unittest.TestCase):

    def test_which(self):
        result = which('python')
        self.assertEqual(result, '/usr/bin/python')
        out, err = shell('which python')
        self.assertEqual(out.strip(), result)

    def test_which_bogus(self):
        result = which('bogus thing does not exist')
        self.assertIsNone(result)
