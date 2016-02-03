from .exc import ErrorStats


class Server(object):
    def __init__(self, client):
        self._client = client._client
        self._endpoint = client._endpoint

    async def ping(self):
        endpoint = "{0}/ping".format(self._endpoint)
        async with self._client.get(endpoint) as r:
            resp = await r.text()
        return resp

    async def stats(self):
        endpoint = "{0}/stats".format(self._endpoint)
        headers = {'content-type': 'application/json'}
        async with self._client.get(endpoint, headers=headers) as r:
            if r.status != 200:
                raise ErrorStats("Stats error. Check configuration riak.")

            resp = await r.json()
        return resp

    async def resources(self):
        headers = {'accept': 'application/json'}
        async with self._client.get(self._endpoint, headers=headers) as r:
            resp = await r.json()
        return resp
