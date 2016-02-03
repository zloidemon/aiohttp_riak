from .exc import NotFound, Error
from aiohttp.errors import ContentEncodingError


class Bucket(object):
    def __init__(self, client, bucket=None):
        self._client = client._client
        self._endpoint = client._endpoint
        self.bucket = bucket
        self.headers = {
            'content-type': 'application/json'
        }
        self.path = "{endpoint}/buckets/{bucket}".format(
                endpoint=client._endpoint, bucket=bucket)

        self.path_keys = lambda k: "{endpoint}/keys/{key}".format(
                endpoint=self.path, key=k)

    async def buckets(self, stream=False):
        if stream:
            stream = "stream"
        else:
            stream = "true"

        endpoint = "{0}/buckets".format(self._endpoint)
        async with self._client.get(endpoint,
                                    headers=self.headers,
                                    params={"buckets": stream}) as r:
            resp = await r.json()
        try:
            return resp['buckets']
        except:
            return []

    async def keys(self, stream=False):
        if stream:
            stream = "stream"
        else:
            stream = "true"

        if not self.bucket:
            raise Error("Keys uses bucket but it is not defined")

        async with self._client.get("{}/keys".format(self.path),
                                    headers=self.headers,
                                    params={"keys": stream}) as r:
            if r.status != 200:
                raise NotFound("Keys in bucket {} not found".format(
                    self.bucket))
            resp = await r.json()

        try:
            return resp['keys']

        except:
            return []

    async def props(self):
        if not self.bucket:
            raise Error("Props uses bucket but it is not defined")

        endpoint = "{bucket}/props".format(bucket=self.path)

        async with self._client.get(endpoint,
                                    headers=self.headers) as r:
            if r.status != 200:
                raise NotFound("Bucket {} not found}".format(self.bucket))
            resp = await r.json()
        try:
            return resp['props']
        except:
            raise Error('No props for {}'.format(self.bucket))

    async def props_del(self):
        """ Fix me after support 204 code in aiohttp """
        endpoint = "{bucket}/props".format(bucket=self.path)

        try:
            async with self._client.delete(endpoint,
                                           headers=self.headers) as r:
                if r.status != 204:
                    raise Error("Bucket {} not found}".format(self.bucket))
                return True
        except ContentEncodingError:
            """ Not error really """
            return True
        except:
            raise

    async def get(self, key, rq='quorum', pr=0,
                  basic_quorum=False, notfound_ok=True):
        if rq not in ['all', 'quorum', 'one']:
            raise Error('Incorrect read quorum): {}', rq)
        params = {
            'r': rq,
            'pr': pr,
            'basic_quorum': basic_quorum,
            'notfound_ok': notfound_ok
        }
        async with self._client.get(self.path_keys(key), params=params) as r:
            resp = await r.text()
            if r.status == 404:
                resp = None

        return resp

    async def index(self, index, start, end=None, max_results=None,
                    continuation=None, stream=False):

        path = "/".join([x for x in
                        [self.path, 'index', index, start, end] if x])

        async with self._client.get(path,
                                    headers=self.headers) as r:
            resp = await r.json()

        try:
            return resp['keys']

        except:
            return []

    async def put(self, key, data, indexes=[]):
        params = {'returnbody': 'true'}

        headers = {}

        for i in indexes:
            i_key = 'x-riak-index-{index}'.format(index=i[0])
            headers[i_key] = i[1]

        headers.update(self.headers)
        async with self._client.put(self.path_keys(key),
                                    headers=headers,
                                    data=data, params=params) as r:
            resp = await r.text()
        return resp

    async def delete(self, key):
        """ Fix me after support 204 code in aiohttp """
        try:
            async with self._client.delete(self.path_keys(key)) as r:
                if r.status not in [204, 404]:
                    return False
                return True
        except ContentEncodingError:
            """ Not error really """
            return True
        except:
            raise
