from django.contrib.auth.models import User
from hashlib import sha1
from base64 import urlsafe_b64encode as safe_encode

class JanrainUser(object):
    """
        This class acts as a quantum container for user data from either the
        Engage or Capture (entity) APIs. Needed properties resolve themselves
        based on the topology of the user_data passed to the constructor.
    """
    def __init__(self, user_data):
        self.data = user_data

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    @property
    def uuid(self):
        """
        A unique code for this user.

        :returns: string
        """
        uuid = self.data.get('uuid')
        if not uuid:
            try:
                uuid = self.data['profile']['identifer']
            except KeyError:
                raise ValueError("Cannot uniquely identify user: %s" % self.data)

        return uuid

    @property
    def hashed(self):
        """
        Uniquely identify this user as a hash.

        :returns: hash string
        """

        # django.contrib.auth.models.User.username is required and
        # has a max_length of 30 so to ensure that we don't go over
        # 30 characters we url-safe base64 encode the sha1 of the identifier
        # returned from janrain and slice `=` from the end.
        # TODO this obviously won't work until user_data is canonicalized
        return safe_encode(sha1(self.uuid).digest())[:-1]

    @property
    def names(self):
        """
        Extracts a name of sorts from this user's data.

        :returns: Tuple of (first_name, last_name). Either may be ''.
        """

        given_name = self.data.get('givenName', '')
        family_name = self.data.get('familyName', '')
        display_name = self.data.get('displayName', '')

        if not any([given_name, family_name, display_name]):
            try:
                names = self.data['profile']['names']
            except KeyError:
                return ('', '')

            given_name = names.get('givenName', '')
            family_name = names.get('familyName', '')
            display_name = names.get('displayName', '')

        return (given_name or display_name, family_name)

    @property
    def email(self):
        """
        Extract an email from user's data if possible.

        :returns: either an email address or ''
        """
        email = self.data.get('email')

        if not email:
            try:
                profile = self.data['profile']
            except KeyError:
                return ''
            email = profile.get('verifiedEmail', '') or profile.get('email', '')

        return email

class JanrainBackend(object):

    def authenticate(self, user_data):
        """
        This function is used to transform a successful response from Janrain
        into an actually authenticated user.

        :param user_data: dictionary of user info from Janrain (either Engage or Capture/Entity)
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
        """
            Must implement this. Deserializes a user id.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def find_user(self, janrain_user):
        """
        Looks up a user in the User table that corresponds to the passed
        JanrainUser.

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
        Creates a User based on janrain_user.

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
