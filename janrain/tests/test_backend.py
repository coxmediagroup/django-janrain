from django.contrib.auth.models import User
import mock
from unittest2 import TestCase

from janrain.backends import JanrainBackend, JanrainUser

class TestJanrainUserEngage(TestCase):
    def setUp(self):
        self.user_data = dict(
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
        self.user = JanrainUser(self.user_data)

    def test_get_names_first_and_last(self):
        fname, lname = self.user.names
        self.assertEqual(fname, 'nate')
        self.assertEqual(lname, 'smith')

    def test_get_names_just_display_no_space(self):
        del self.user_data['profile']['name']['givenName']
        del self.user_data['profile']['name']['familyName']
        user = JanrainUser(self.user_data)
        fname, lname = user.names
        self.assertEqual(fname, 'nathanielksmith')
        self.assertEqual(lname, '')

    def test_get_names_no_names(self):
        del self.user_data['profile']['name']['givenName']
        del self.user_data['profile']['name']['familyName']
        del self.user_data['profile']['displayName']
        user = JanrainUser(self.user_data)
        fname, lname = user.names
        self.assertEqual(fname, '')
        self.assertEqual(lname, '')

    def get_email(self):
        del self.user_data['profile']['verifiedEmail']
        user = JanrainUser(self.user_data)
        self.assertEqual(user.email, 'nate.smith@coxinc.com')

    def get_verified_email(self):
        self.assertEqual(self.user.email, 'nathanielksmith@gmail.com')

    def get_no_email(self):
        del self.user_data['profile']['verifiedEmail']
        del self.user_data['profile']['email']
        user = JanrainUser(self.user_data)
        self.assertEqual(user.email, '')

# repeat above but for capture (entity) style data
class TestJanrainUserCapture(TestCase):
    def setUp(self):
        self.user_data = dict(
            uuid='123456789',
            givenName='nate',
            familyName='smith',
            displayName='nathanielksmith',
            email='nate.smith@coxinc.com',
        )
        self.user = JanrainUser(self.user_data)

    def test_get_names_first_and_last(self):
        fname, lname = self.user.names
        self.assertEqual(fname, 'nate')
        self.assertEqual(lname, 'smith')

    def test_get_names_just_display_no_space(self):
        del self.user_data['givenName']
        del self.user_data['familyName']
        user = JanrainUser(self.user_data)
        fname, lname = user.names
        self.assertEqual(fname, 'nathanielksmith')
        self.assertEqual(lname, '')

    def test_get_names_no_names(self):
        del self.user_data['givenName']
        del self.user_data['familyName']
        del self.user_data['displayName']
        user = JanrainUser(self.user_data)
        fname, lname = user.names
        self.assertEqual(fname, '')
        self.assertEqual(lname, '')

    def get_email(self):
        self.assertEqual(self.user.email, 'nate.smith@coxinc.com')

    def get_no_email(self):
        del self.user_data['email']
        user = JanrainUser(self.user_data)
        self.assertEqual(user.email, '')

class TestBackend(TestCase):
    def setUp(self):
        self.backend = JanrainBackend()
        muser = mock.Mock()
        muser.DoesNotExist = User.DoesNotExist
        muser.objects = mock.Mock()
        muser.objects.get = mock.Mock()
        self.muser = muser

        self.janrain_user = mock.Mock()

    def test_find_user_found(self):
        with mock.patch('janrain.backends.User', self.muser):
            self.muser.objects.get.return_value = True
            self.assertTrue(self.backend.find_user(self.janrain_user))

    def test_find_user_not_found(self):
        with mock.patch('janrain.backends.User', self.muser):
            self.muser.objects.get.side_effect = self.muser.DoesNotExist
            self.assertEqual(self.backend.find_user(self.janrain_user), None)

