from django.contrib.auth.models import User
from hashlib import sha1
from base64 import urlsafe_b64encode as safe_encode

class JanrainUser(object):
    def __new__(self,user_data):
        # TODO create canonical user_data
        self.user_data = dict()
        if 'profile' in user_data:
            # engage/auth_info case
            pass
        else:
            # capture/entity case
            pass

    @property
    def hashed(self):
        """
        Uniquely identify this user as a hash.
        :returns: hash string
        """
        raise NotImplemented
        # django.contrib.auth.models.User.username is required and
        # has a max_length of 30 so to ensure that we don't go over
        # 30 characters we url-safe base64 encode the sha1 of the identifier
        # returned from janrain and slice `=` from the end.
        # TODO this obviously won't work until user_data is canonicalized
        return safe_encode(sha1(self.data['profile']['identifier']).digest())[:-1]

    @property
    def names(self):
        """
        Extracts a name of sorts from this user's data.

        :returns: Tuple of (first_name, last_name). Either may be ''.
        """
        raise NotImplemented
        # TODO this is a mess. I'll probably change it after working with some
        # actual data.
        profile = self.user_data['profile']
        names = profile.get('name')
        if type(names) == dict: # TODO is this type check really needed?
            # attempt to extract something like a first and last name
            given_name = names.get('givenName', '')
            display_name = profile.get('displayName', '')
            family_name = names.get('familyName', '')

            return (given_name or display_name, family_name)

    @property
    def email(self):
        raise NotImplemented
        """
        Extract an email from user's data if possible.

        :returns: either an email address or ''
        """
        profile = self.user_data['profile']
        return profile.get('verifiedEmail') or profile.get('email') or ''

class JanrainBackend(object):

    def authenticate(self, user_data):
        """
        This function is used to transform a successful response from Janrain
        into an actually authenticated user.

        :param auth_info: dictionary of user info from Janrain
        :returns: User, either one found in the database or a new one
        """

        janrain_user = JanrainUser(user_data)
        # Being here means janrain was able to log in this user. We may or
        # may not know about this user yet; use find_user to check. If
        # they're new, hand their info to create_user to add a new User.
        user = self.find_user(janrain_user)

        if not user:
            user = self.create_user(janrain_user)

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def find_user(self, janrain_user):
        """
        Looks up a user in the User table based on auth_info.

        This is intended to be overridden.

        :param janrain_user: JanrainUser
        :returns: Either None or User
        """
        try:
            return User.objects.get(username=janrain_user.hashed)
        except User.DoesNotExist:
            return None

    def create_user(self, janrain_user):
        """
        Creates a User based on auth_info.

        This is intended to be overridden.

        :param janrain_user: JanrainUser
        :returns: User
        """
        fn, ln = janrain_user.names
        u = User(
                username=janrain_user.hashed,
                password='',
                first_name=fn,
                last_name=ln,
                email=janrain_user.email
            )

        # Set an unusable password to protect unauthorized access.
        u.set_unusable_password()
        u.is_active = True
        u.is_staff = False
        u.is_superuser = False
        u.save()

        return u
