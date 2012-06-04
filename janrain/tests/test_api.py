import json
import mock
from unittest2 import TestCase

from janrain.api import JanrainClient

class MockRequestsJsonResponse(object):
    def __init__(self, data):
        self.text = json.dumps(data)

class TestAPI(TestCase):
    def setUp(self):
        self.client = JanrainClient('test_key', endpoint='test_endpoint')
        self.reqs = mock.Mock()


    def test__make_request_get(self):
        self.reqs.get = mock.Mock(return_value=MockRequestsJsonResponse(dict(hello='there')))
        with mock.patch('janrain.api.requests', self.reqs):
            response = self.client._make_request('path')

            self.assertEqual(len(response.keys()), 1, 'got back our json')
            self.assertEqual(response['hello'], 'there', 'got back our json')

    def test__make_request_post(self):
        self.reqs.post = mock.Mock(return_value=MockRequestsJsonResponse(dict(you='guys')))
        with mock.patch('janrain.api.requests', self.reqs):
            response = self.client._make_request('path', method='post')

            self.assertEqual(len(response.keys()), 1, 'got back our json')
            self.assertEqual(response['you'], 'guys', 'got back our json')

    def test__make_request_bad_method(self):
        self.assertRaises(ValueError, self.client._make_request, 'path', method='foobarbaz')

    def test_auth_info(self):
        pass
