aiohttp_riak
============
.. image:: https://travis-ci.org/zloidemon/aiohttp_riak.svg?branch=master
    :target: https://travis-ci.org/zloidemon/aiohttp_riak
.. image:: https://coveralls.io/repos/zloidemon/aiohttp_riak/badge.svg
    :target: https://coveralls.io/r/zloidemon/aiohttp_riak
.. image:: https://badge.fury.io/py/aiohttp_riak.svg
    :target: https://badge.fury.io/py/aiohttp_riak

riakhttp_ protocol implementation for `aiohttp.web`__.

__ aiohttp_web_


Example
-------

.. code:: python

    import asyncio
    import aiohttp
    from aiohttp_riak import RiakHTTP, Bucket

    async def riak_requests(client):
        bucket = Bucket(client, 'example')

        # Secondary indexes
        indexes = [
            ('example_bin', 'ex'),
            ('example_int', '1')
        ]
        await bucket.put('key', 'val', [indexes[0]])
        await bucket.put('key2', 'val2', [indexes[1]])
        await bucket.put('key3', 'val3', indexes)

        keys = await bucket.keys()
        print('KEYS', keys)

        keys = await bucket.index('example_bin', 'ex')
        print('INDEX_BIN', keys)

        keys = await bucket.index('example_int', '1')
        print('INDEX_INT', keys)


        print('GET', await bucket.get('key2'))
        print('DEL', await bucket.delete('key2'))
        print('GET', await bucket.get('key2'))

        print('BUCKETS', await bucket.buckets())
        print('PING', await client.ping())

        props = await bucket.props()
        print('PROPS', props)

    loop = asyncio.get_event_loop()
    rh = RiakHTTP('127.0.0.1',loop=loop)

    content = loop.run_until_complete(
        riak_requests(rh))

    rh.close()

License
-------

``aiohttp_riak`` BSD license.


.. _riakhttp: http://docs.basho.com/riak/1.4.12/dev/references/http
.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html
