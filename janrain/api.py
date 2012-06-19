from functools import partial
import json
import requests
import urlparse

class JanrainClient(object):
    def __init__(self, api_key, endpoint='https://rpxnow.com/api/v2/'):
        self.url = endpoint
        self.api_key = api_key

    def auth_info(self, token):
        return self._make_request('auth_info', data=dict(token=token))

    # TODO you know, the rest of the API.

    def _make_request(self, path, method='get', data={}):
        """
            Actually make a web request.
        """
        data['apiKey'] = data.get('api_key', self.api_key)
        method = method.lower()
        full_url = urlparse.urljoin(self.url, path)

        try:
            hit_url = partial(getattr(requests, method), full_url)
        except AttributeError:
            raise ValueError("Invalid HTTP method %s" % method)

        kwargs = {}
        key = 'params' if method == 'get' else 'data'
        kwargs[key] = data

        return json.loads(hit_url(**kwargs).content)
