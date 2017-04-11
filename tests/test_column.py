from tests import setup_lib_path; setup_lib_path()

from misc.column import column
import color
import unittest


class ColumnTest(unittest.TestCase):

    def test_column(self):
        rows = [
           ['a',          'b',        'c', 'd'],
           ['aaaaaaaaaa', 'b',        'c', 'd'],
           ['a',          'bbbbbbbb', 'c', 'd'],
        ]
        result = column(rows)
        expected = [
            'a           b         c  d',
            'aaaaaaaaaa  b         c  d',
            'a           bbbbbbbb  c  d',
        ]
        self.assertEqual(result, expected)

    def test_column_no_padding(self):
        rows = [
           ['a',          'b',        'c', 'd'],
           ['aaaaaaaaaa', 'b',        'c', 'd'],
           ['a',          'bbbbbbbb', 'c', 'd'],
        ]
        result = column(rows, padding=0)
        expected = [
            'a         b       cd',
            'aaaaaaaaaab       cd',
            'a         bbbbbbbbcd',
        ]
        self.assertEqual(result, expected)

    def test_column_custom_padding(self):
        rows = [
           ['a',          'b',        'c', 'd'],
           ['aaaaaaaaaa', 'b',        'c', 'd'],
           ['a',          'bbbbbbbb', 'c', 'd'],
        ]
        result = column(rows, padding=1, delimiter='|')
        expected = [
            'a         |b       |c|d',
            'aaaaaaaaaa|b       |c|d',
            'a         |bbbbbbbb|c|d',
        ]
        self.assertEqual(result, expected)

    def test_column_colored(self):
        rows = [
           [color.red('a'),          'b',        'c', 'd'],
           ['aaaaaaaaaa', 'b',        'c', 'd'],
           ['a',          'bbbbbbbb', 'c', 'd'],
        ]
        result = column(rows)
        expected = [
           '{}           b         c  d'.format(color.red('a')),
            'aaaaaaaaaa  b         c  d',
            'a           bbbbbbbb  c  d',
        ]
        self.assertEqual(result, expected)
