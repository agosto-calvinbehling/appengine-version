from misc.shell import shell
from misc.which import which
from gae_version import print_data_table
from gae_version import generate_human_array
import json
import unittest
import StringIO


expected_result = """
INDEX  VERSION                      frontend  default  refresh  content  migration  backup
0      11-88f89eb760                                                     -           
1      11-ddd271af2f                                                     -           
2      12-ddd271af2f                                                     -           
3      274-1dd9cba6a4                                                    -           
4      274-b57f1b50e7                                                    -           
5      277-3adf4e6118                                                    -           
6      277-d91744cc08                                                    -           
7      293-cecb1aef42                                                    -          -
8      310-982e38b9a1                                                    -          -
9      313-9-9f65c9cdcb             -         -                 -        -          -
10     317-7e668b2b43               -         -        -        -        -          -
11     322-b354b87888               -         -        -        -        -          -
12     ah-builtin-datastoreservice            -                                      
13     ah-builtin-python-bundle               -                                      
14     ci                           -         -        -        -        -          -
15     ci-0ba28e6705                                                     -           
16     ci-a7ff89b102                                                     -           
17     ci-ba7463c40f                                                     -           
18     ci-ea4ecddf75                                                     -           
19     ci2                          -         -        -        -        -          -
20     dummy-69311cd6ea             +         +        +        +        +          +
21     karlktest                                                         -           
22     raytest-59e3abcdcd           -         -                 -        -          -
23     snapshot                                                                     -
24     test-single                                     -
"""

expected_table = [
    ['INDEX', 'VERSION', 'frontend', 'default', 'refresh', 'content', 'migration', 'backup'],
    [0,                u'11-88f89eb760', ' ', ' ', ' ', ' ', '-', ' '],
    [1,                u'11-ddd271af2f', ' ', ' ', ' ', ' ', '-', ' '],
    [2,                u'12-ddd271af2f', ' ', ' ', ' ', ' ', '-', ' '],
    [3,               u'274-1dd9cba6a4', ' ', ' ', ' ', ' ', '-', ' '],
    [4,               u'274-b57f1b50e7', ' ', ' ', ' ', ' ', '-', ' '],
    [5,               u'277-3adf4e6118', ' ', ' ', ' ', ' ', '-', ' '],
    [6,               u'277-d91744cc08', ' ', ' ', ' ', ' ', '-', ' '],
    [7,               u'293-cecb1aef42', ' ', ' ', ' ', ' ', '-', '-'],
    [8,               u'310-982e38b9a1', ' ', ' ', ' ', ' ', '-', '-'],
    [9,             u'313-9-9f65c9cdcb', '-', '-', ' ', '-', '-', '-'],
    [10,              u'317-7e668b2b43', '-', '-', '-', '-', '-', '-'],
    [11,              u'322-b354b87888', '-', '-', '-', '-', '-', '-'],
    [12, u'ah-builtin-datastoreservice', ' ', '-', ' ', ' ', ' ', ' '],
    [13,    u'ah-builtin-python-bundle', ' ', '-', ' ', ' ', ' ', ' '],
    [14,                          u'ci', '-', '-', '-', '-', '-', '-'],
    [15,               u'ci-0ba28e6705', ' ', ' ', ' ', ' ', '-', ' '],
    [16,               u'ci-a7ff89b102', ' ', ' ', ' ', ' ', '-', ' '],
    [17,               u'ci-ba7463c40f', ' ', ' ', ' ', ' ', '-', ' '],
    [18,               u'ci-ea4ecddf75', ' ', ' ', ' ', ' ', '-', ' '],
    [19,                         u'ci2', '-', '-', '-', '-', '-', '-'],
    [20,            u'dummy-69311cd6ea', '+', '+', '+', '+', '+', '+'],
    [21,                   u'karlktest', ' ', ' ', ' ', ' ', '-', ' '],
    [22,          u'raytest-59e3abcdcd', '-', '-', ' ', '-', '-', '-'],
    [23,                    u'snapshot', ' ', ' ', ' ', ' ', ' ', '-'],
    [24,                 u'test-single', ' ', ' ', '-', ' ', ' ', ' '],
]


def get_raw_data():
    with open('test_data/appcfg_list_versions.json') as f:
        data = json.loads(f.read())
    return data


class GaeVersionTest(unittest.TestCase):
    # result = generate_human_array(data, current)
    # csv_data = to_csv(result)
    # output = generate_table(csv_data)

    def test_which_shell_python(self):
        result = which('python')
        self.assertEqual(result, '/usr/bin/python')
        out, err = shell('which python')
        self.assertEqual(out.strip(), result)

    def test_which_bogus(self):
        result = which('bogus thing does not exist')
        self.assertIsNone(result)

    def test_data(self):
        data = get_raw_data()
        current = {}
        for key in data.keys():
            current[key] = 'dummy-69311cd6ea'
        output_file = StringIO.StringIO()
        print_data_table(data, current, output_file)
        result = output_file.getvalue()
        output_file.close()
        split_expected = expected_result.split('\n')[1:]
        split_result = result.replace('\r', '').split('\n')
        try:
            self.assertEqual(split_expected, split_result)
        except:
            print(expected_result)
            print(result)
            raise

    def test_generate(self):
        data = get_raw_data()
        current = {}
        for key in data.keys():
            current[key] = 'dummy-69311cd6ea'
        result = generate_human_array(data, current)
        self.assertEqual(expected_table, result)
