import unittest
from misc.groupby import groupby, multi_groupby, multi_groupby_single_value
import json


def get_ungrouped_data():
    with open('test_data/ungrouped.json') as f:
        data = json.loads(f.read())
    return data


class GroupbyTest(unittest.TestCase):
    def setUp(self):
        super(GroupbyTest, self).setUp()
        self.ungrouped = get_ungrouped_data()

    def test_ungrouped_data(self):
        self.assertEqual(len(self.ungrouped), 136)
        for item in self.ungrouped:
            self.assertTrue('id' in item)
            self.assertTrue('service' in item)
            self.assertTrue('traffic_split' in item)

    def test_groupby(self):
        key = 'id'
        grouped = groupby(self.ungrouped, key)
        for outer_key, data in grouped.iteritems():
            self.assertTrue(isinstance(data, list))
            for item in data:
                self.assertEqual(outer_key, item[key])

    def test_multi_groupby(self):
        keys = ('id', 'service')
        grouped = multi_groupby(self.ungrouped, *keys)
        for id_key, id_data in grouped.iteritems():
            for service_key, service_data in id_data.iteritems():
                self.assertTrue(isinstance(service_data, list))
                for item in service_data:
                    self.assertEqual(id_key, item['id'])
                    self.assertEqual(service_key, item['service'])

    def test_multi_groupby_sv(self):
        keys = ('id', 'service')
        grouped = multi_groupby_single_value(self.ungrouped, keys, 'traffic_split')
        for id_key, id_data in grouped.iteritems():
            for service_key, service_data in id_data.iteritems():
                self.assertTrue(isinstance(service_data, (int, float)))
                if id_key == 'new-hash-test-6a8e9dd99a':
                    self.assertEqual(service_data, 1)
                else:
                    self.assertEqual(service_data, 0)

    def test_multi_groupby_sv_modules(self):
        keys = ('service', 'id')
        grouped = multi_groupby_single_value(self.ungrouped, keys, 'traffic_split')
        self.assertEqual(sorted(grouped.keys()), sorted(['refresh', 'frontend', 'default', 'migration', 'backup', 'content']))
        versions = set().union(*grouped.values())
        self.assertEqual(versions, {
            '320-1-7ef044fd58',
            '320-2-aac3d5f825',
            '321-0-fff9f9e2ab',
            '322-0-c250d16724',
            '324-0-96f30f94b7',
            '325-1-28afd7b4fb',
            '325-2-9be3162894',
            '325-3-29bde01e75',
            '325-4-dee996d65d',
            '325-5-a89ccc57f3',
            '325-6-984089c489',
            '325-7-47492d95f3',
            '325-7-545350267a',
            '325-8-af54de1f4a',
            '326-2c22c74d0a',
            '327-0-9c1016fd1a',
            '328-0-c135f9e6a8',
            'ereport-test-caedc56daf',
            'fb-minify-spike-f8977bd6452174ecb5fcfdd1db5f9306fea40bc9',
            'fb-spike-7e2496e5a0',
            'firebase-test2-5bb0798999',
            'firebase-test3-4948fa7aa2',
            'login-test-898b03f7e6',
            'login-test-fix-47b13dc4db',
            'new-hash-test-6a8e9dd99a',
            'new-hash-test-kris-6a8e9dd99a'}
        )
