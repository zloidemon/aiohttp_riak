import asyncio
import unittest
from uuid import uuid4
from data import DATA
import json
from aiohttp_riak import RiakHTTP, Bucket


class TestRiak(unittest.TestCase):

    def setUp(self):
        self._index = 'elastic_search'
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.riak = RiakHTTP('127.0.0.1', loop=self.loop)
        self.bucket = Bucket(self.riak, 'tests')
        self.addCleanup(self.riak.close)
        try:
            self.loop.run_until_complete(self.cleanRiak())
        except:
            pass

    async def cleanRiak(self):
        data = await self.bucket.keys()
        for d in data:
            ret = await self.bucket.delete(d)
            self.assertTrue(ret)

    def tearDown(self):
        self.loop.run_until_complete(self.cleanRiak())
        self.loop.close()

    def test_server(self):
        async def go():
            ret = await self.riak.ping()
            self.assertEqual('OK', ret)
            ret = await self.riak.stats()
            self.assertIsNotNone(ret)
            ret = await self.riak.resources()
            self.assertIsNotNone(ret)
        self.loop.run_until_complete(go())

    def test_keys(self):
        async def go():
            for country in DATA:
                jdata = json.dumps(DATA[country])
                await self.bucket.put(country, jdata)
                ret = await self.bucket.get(country)
                self.assertEqual(jdata, ret)
        self.loop.run_until_complete(go())

    def test_props(self):
        async def go():
            ret = await self.bucket.props()
            self.assertEqual('quorum', ret['r'])
            self.assertEqual('quorum', ret['w'])
            self.assertEqual('quorum', ret['dw'])
            self.assertEqual('quorum', ret['rw'])
            self.assertIs(3, ret['n_val'])
            self.assertFalse(ret['basic_quorum'])
            self.assertFalse(ret['last_write_wins'])
            self.assertFalse(ret['allow_mult'])
            self.assertEqual('tests', ret['name'])
            self.assertEqual([], ret['precommit'])
            self.assertEqual([], ret['postcommit'])

            ret = await self.bucket.props_del()
            self.assertTrue(ret)
        self.loop.run_until_complete(go())

    def test_buckets(self):
        async def go():
            ret = await self.bucket.buckets()
            self.assertIs(0, len(ret))
        self.loop.run_until_complete(go())

    def test_put(self):
        async def go():
            for country in DATA:
                for region in DATA[country]:
                    indexes = [
                        ('country_bin', country),
                        ('region_int', '{}'.format(len(region)))
                    ]
                    ret = await self.bucket.put(uuid4().hex, region, indexes)
                    self.assertEqual(region, ret)
            DDR = await self.bucket.index('country_bin', 'DDR')
            self.assertIs(15, len(DDR))
            USSR = await self.bucket.index('country_bin', 'СССР')
            self.assertIs(15, len(USSR))
            ret = await self.bucket.index('region_int', '3', '6')
            self.assertIs(6, len(ret))
            ret = await self.bucket.index('region_int', '7', '20')
            self.assertIs(24, len(ret))
        self.loop.run_until_complete(go())

    def test_delete(self):
        async def go():
            ret = await self.bucket.put('Ivanov', 'Ivan')
            self.assertEqual('Ivan', ret)
            ret = await self.bucket.delete('Ivanov')
            self.assertTrue(ret)
            ret = await self.bucket.delete('Ivanov')
            self.assertTrue(ret)
        self.loop.run_until_complete(go())
