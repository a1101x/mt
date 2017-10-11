from django.contrib.auth import get_user_model


User = get_user_model()


class EmailOrUsernameModelBackend(object):
    """
    Custom backend for authentication.
    Can login with username or email.
    """
    def authenticate(self, username=None):
        """
        Auth method using both username and email.
        """
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}

        try:
            user = User.objects.get(**kwargs)
        except User.DoesNotExist:
            return None

    def get_user(self, username):
        """
        Get user with username.
        """
        try:
            return User.objects.get(pk=username)
        except User.DoesNotExist:
            return None
