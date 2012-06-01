import mock
from unitttest2 import TestCase

from janrain.api import JanrainClient

class TestAPI(TestCase):
    def setUp(self):
        self.client = JanrainClient('test_key', 'test_endpoint')
