from django.contrib.auth.models import User
from hashlib import sha1
from base64 import urlsafe_b64encode as safe_encode

class JanrainBackend(object):

    def authenticate(self, auth_info):
        """
        This function is used to transform a successful response from Janrain
        into an actually authenticated user.

        :param auth_info: dictionary of user info from Janrain
        :returns: User, either one found in the database or a new one
        """
        # Being here means janrain was able to log in this user. We may or
        # may not know about this user yet; use find_user to check. If
        # they're new, hand their info to create_user to add a new User.
        u = self.find_user(auth_info)

        if not u:
            u = self.create_user(auth_info)

        return u

    def find_user(self, auth_info):
        """
        Looks up a user in the User table based on auth_info

        :param auth_info: auth_info from Janrain
        :returns: Either None or User
        """
        try:
            return User.objects.get(username=self.hash_user(auth_info))
        except User.DoesNotExist:
            return None

    def create_user(self, auth_info):
        """
        Creates a User based on auth_info.

        :param auth_info: auth_info from Janrain
        :returns: User
        """
        fn, ln = self.get_names(auth_info)
        u = User(
                username=self.hash_user(auth_info),
                password='',
                first_name=fn,
                last_name=ln,
                email=self.get_email(auth_info)
            )

        # Set an unusable password to protect unauthorized access.
        u.set_unusable_password()
        u.is_active = True
        u.is_staff = False
        u.is_superuser = False
        u.save()

        return u

    def hash_user(self, auth_info):
        """
        Uniquely identify the user represented by auth_info as a hash.

        :param auth_info: auth_info from Janrain
        :returns: hash string
        """
        # django.contrib.auth.models.User.username is required and 
        # has a max_length of 30 so to ensure that we don't go over 
        # 30 characters we url-safe base64 encode the sha1 of the identifier 
        # returned from janrain and slice `=` from the end.
        return safe_encode(sha1(auth_info['profile']['identifier']).digest())[:-1]

    def get_names(self, auth_info):
        """
        Extracts a name of sorts from some auth_info.

        :param auth_info: auth_info from Janrain
        :returns: Tuple of (first_name, last_name). Either may be ''.
        """
        p = auth_info['profile']
        nt = p.get('name')
        if type(nt) == dict:
            fname = nt.get('givenName')
            lname = nt.get('familyName')
            if fname and lname:
                return (fname, lname)
        dn = p.get('displayName')
        if len(dn) > 1 and dn.find(' ') != -1:
            (fname, lname) = dn.split(' ', 1)
            return (fname, lname)
        elif dn == None:
            return ('', '')
        else:
            return (dn, '')

    def get_email(self, auth_info):
        """
        Extract an email from auth_info, if possible.

        :param auth_info: auth_info from Janrain
        :returns: either an email address or ''
        """
        p = auth_info['profile']
        return p.get('verifiedEmail') or p.get('email') or ''

