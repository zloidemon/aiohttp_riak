import aiohttp
from .Server import Server


class RiakHTTP:
    def __init__(self, host='127.0.0.1', port=8098, loop=None):
        self._client = aiohttp.ClientSession(loop=loop)
        self._endpoint = "http://{host}:{port}".format(
                            host=host, port=port)

    async def ping(self):
        return await Server(self).ping()

    async def stats(self):
        return await Server(self).stats()

    async def resources(self):
        return await Server(self).resources()

    def close(self):
        self._client.close()
