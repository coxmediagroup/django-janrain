from django.contrib.auth.models import User
import mock
from unittest2 import TestCase

from janrain.backends import JanrainBackend

class TestBackend(TestCase):
    def setUp(self):
        self.backend = JanrainBackend()
        self.auth_info = dict(
            profile=dict(
                identifier='123456789',
                name=dict(
                    # a maximal case; we'll override in tests
                    givenName='nate',
                    familyName='smith',
                ),
                displayName='nathanielksmith',
                verifiedEmail='nathanielksmith@gmail.com',
                email='nate.smith@coxinc.com'
            ),
        )
        muser = mock.Mock()
        muser.DoesNotExist = User.DoesNotExist
        muser.objects = mock.Mock()
        muser.objects.get = mock.Mock()
        self.muser = muser

    def test_find_user_found(self):
        with mock.patch('janrain.backends.User', self.muser):
            self.muser.objects.get.return_value = True
            self.assertTrue(self.backend.find_user(self.auth_info))

    def test_find_user_not_found(self):
        with mock.patch('janrain.backends.User', self.muser):
            self.muser.objects.get.side_effect = self.muser.DoesNotExist
            self.assertEqual(self.backend.find_user(self.auth_info), None)

    def test_get_names_first_and_last(self):
        fname, lname = self.backend.get_names(self.auth_info)
        self.assertEqual(fname, 'nate')
        self.assertEqual(lname, 'smith')

    def test_get_names_just_display_with_space(self):
        del self.auth_info['profile']['name']['givenName']
        del self.auth_info['profile']['name']['familyName']
        self.auth_info['profile']['displayName'] = 'nathaniel smith'

        fname, lname = self.backend.get_names(self.auth_info)
        self.assertEqual(fname, 'nathaniel')
        self.assertEqual(lname, 'smith')

    def test_get_names_just_display_no_space(self):
        del self.auth_info['profile']['name']['givenName']
        del self.auth_info['profile']['name']['familyName']

        fname, lname = self.backend.get_names(self.auth_info)
        self.assertEqual(fname, 'nathanielksmith')
        self.assertEqual(lname, '')

    def test_get_names_no_names(self):
        del self.auth_info['profile']['name']['givenName']
        del self.auth_info['profile']['name']['familyName']
        del self.auth_info['profile']['displayName']

        fname, lname = self.backend.get_names(self.auth_info)
        self.assertEqual(fname, '')
        self.assertEqual(lname, '')

    def get_email(self):
        del self.auth_info['profile']['verifiedEmail']

        email = self.backend.get_email(self.auth_info)
        self.assertEqual(email, 'nate.smith@coxinc.com')

    def get_verified_email(self):
        email = self.backend.get_email(self.auth_info)
        self.assertEqual(email, 'nathanielksmith@gmail.com')

    def get_no_email(self):
        del self.auth_info['profile']['verifiedEmail']
        del self.auth_info['profile']['email']

        email = self.backend.get_email(self.auth_info)
        self.assertEqual(email, '')
