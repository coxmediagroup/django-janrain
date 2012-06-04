import mock
from unittest2 import TestCase

class TestBackend(TestCase):
    def setUp(self):
        self.auth_info = dict(
            profile=dict(
                identifier='123456789',
                name=dict(
                    # a maximal case; we'll override in tests
                    givenName='nate',
                    familyName='smith',
                    displayName='nathanielksmith'
                ),
                verifiedEmail='nathanielksmith@gmail.com',
                email='nate.smith@coxinc.com'
            ),
        )
        muser = mock.Mock()
        muser.objects = mock.Mock()
        muser.objects.get = mock.Mock()
        self.muser = muser

    def test_authenticate(self):
        pass

    def test_create_user(self):
        pass

    def test_find_user(self):
        pass

    def test_get_names_first_and_last(self):
        pass

    def test_get_names_just_display(self):
        pass

    def get_email(self):
        pass
