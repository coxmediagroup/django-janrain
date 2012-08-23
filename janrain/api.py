from functools import partial
import json
import requests
import urlparse

class APIException(Exception):
    def __init__(self, method, response):
        self.method = method
        self.response = response

    def __str__(self):
        return "janrain %s return error response: %s" % (self.method, json.dumps(self.response))


class JanrainClient(object):
    APIException = APIException

    def __init__(self, api_key, client_id, client_secret, endpoint='https://rpxnow.com/api/v2/'):
        self.url = endpoint
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret

    # Capture - Oauth
    def oauth_token(self, code, redirect_uri, grant_type='authorization_code'):
        return self._make_request('oauth/token', method='post', data=dict(
            code=code,
            redirect_uri=redirect_uri,
            grant_type=grant_type,
            client_id=self.client_id,
            client_secret=self.client_secret
        ))

    # Capture - Entity
    def entity(self, uuid=None, type_name=None, access_token=None):
        if access_token:
            return self._make_request('entity',
                headers=dict(Authorization='OAuth %s' % access_token)
            )
        elif all([self.client_id, self.client_secret, type_name, uuid]):
            # TODO support other way to call entity
            return self._make_request('entity', method='post', data=dict(
                client_id=self.client_id,
                client_secret=self.client_secret,
                type_name=type_name,
                uuid=uuid
            ))
        else:
            raise ValueError('Bad invocation of entity; needs either (client_id and client_secret) or access_token')

    def entity_update(self, uuid, type_name, update):
        return self._make_request('entity.update', method='post', data=dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            type_name=type_name,
            uuid=uuid,
            value=json.dumps(update)
        ))

    # Engage
    def auth_info(self, token):
        return self._make_request('auth_info', data=dict(token=token))

    # Engage - Mappings
    def map(self, identifier, primary_key, overwrite=True):
        return self._make_request('map', method='post', data=dict(
            identifier=identifier,
            primaryKey=primary_key,
            overwrite='true' if overwrite else 'false'
        ))

    # TODO you know, the rest of the API.

    def _make_request(self, path, method='get', data={}, headers={}):
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

        kwargs = dict(headers=headers)
        key = 'params' if method == 'get' else 'data'
        kwargs[key] = data

        response = hit_url(**kwargs)
        return json.loads(response.content)
