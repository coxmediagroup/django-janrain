import json
import mock
from unittest2 import TestCase

from janrain.api import JanrainClient

class MockRequestsJsonResponse(object):
    def __init__(self, data):
        self.content = json.dumps(data)

class TestAPI(TestCase):
    def setUp(self):
        self.client = JanrainClient(client_id=1, client_secret=2, api_url='test_endpoint')
        self.reqs = mock.Mock()


    def test__make_request_get(self):
        self.reqs.get = mock.Mock(return_value=MockRequestsJsonResponse(dict(hello='there')))
        with mock.patch('janrain.api.requests', self.reqs):
            response = self.client._make_request('path')

            self.assertEqual(len(response.keys()), 1, 'got back our json')
            self.assertEqual(response['hello'], 'there', 'got back our json')

    def test__make_request_get_args(self):
        self.reqs.get = mock.Mock(return_value=MockRequestsJsonResponse(dict(hello='there')))
        with mock.patch('janrain.api.requests', self.reqs):
            self.client._make_request('path', data=dict(ohno='youdidnt'))
            self.reqs.get.assert_called_with('path', headers=dict(), params=dict(ohno='youdidnt'))

    def test__make_request_post(self):
        self.reqs.post = mock.Mock(return_value=MockRequestsJsonResponse(dict(you='guys')))
        with mock.patch('janrain.api.requests', self.reqs):
            response = self.client._make_request('path', method='post')

            self.assertEqual(len(response.keys()), 1, 'got back our json')
            self.assertEqual(response['you'], 'guys', 'got back our json')

    def test__make_request_post_args(self):
        self.reqs.post = mock.Mock(return_value=MockRequestsJsonResponse(dict(you='guys')))
        with mock.patch('janrain.api.requests', self.reqs):
            self.client._make_request('path', method='post', data=dict(ohno='youdidnt'))
            self.reqs.post.assert_called_with('path', headers=dict(), data=dict(ohno='youdidnt'))

    def test__make_request_bad_method(self):
        self.assertRaises(ValueError, self.client._make_request, 'path', method='foobarbaz')

    def test__make_request_headers(self):
        self.reqs.post = mock.Mock(return_value=MockRequestsJsonResponse(dict(you='guys')))
        with mock.patch('janrain.api.requests', self.reqs):
            self.client._make_request('path', method='post', headers=dict(Authorization="oauth"), data=dict(ohno='youdidnt'))
            self.reqs.post.assert_called_with('path', headers=dict(Authorization="oauth"), data=dict(ohno='youdidnt'))

    def test_clients_add_no_features(self):
        self.reqs.post = mock.Mock(return_value=MockRequestsJsonResponse(dict(hello='there')))
        with mock.patch('janrain.api.requests', self.reqs):
            resp = self.client.clients_add('description')
            self.assertEqual(resp['hello'], 'there', 'got back our json')
            self.reqs.post.assert_called_with('clients/add', headers={}, data=dict(
                client_id=1,
                client_secret=2,
                description='description'
            ))

    def test_clients_add_with_features(self):
        self.reqs.post = mock.Mock(return_value=MockRequestsJsonResponse(dict(hello='there')))
        with mock.patch('janrain.api.requests', self.reqs):
            resp = self.client.clients_add('description', ["feature"])
            self.assertEqual(resp['hello'], 'there', 'got back our json')
            self.reqs.post.assert_called_with('clients/add', headers={}, data=dict(
                client_id=1,
                client_secret=2,
                features='["feature"]',
                description='description'
            ))

    def test_settings_set_multi(self):
        self.reqs.post = mock.Mock(return_value=MockRequestsJsonResponse(dict(hello='there')))
        with mock.patch('janrain.api.requests', self.reqs):
            resp = self.client.settings_set_multi('for_client_id', {'setting': 'value'})
            self.assertEqual(resp['hello'], 'there', 'got back our json')
            self.reqs.post.assert_called_with('settings/set_multi', headers={}, data=dict(
                client_id=1,
                client_secret=2,
                for_client_id='for_client_id',
                items='{"setting": "value"}',
            ))

    def test_clients_list(self):
        self.reqs.get = mock.Mock(return_value=MockRequestsJsonResponse(dict(hello='there')))
        with mock.patch('janrain.api.requests', self.reqs):
            resp = self.client.clients_list()
            self.assertEqual(resp['hello'], 'there', 'got back our json')
            self.reqs.get.assert_called_with('clients/list', headers={}, params=dict(
                client_id=1,
                client_secret=2,
            ))
