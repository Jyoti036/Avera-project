from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Authenticate against settings.AUTH_USER_MODEL using email.
    """
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        # Support both 'email' and 'username' kwargs
        lookup_email = email or username or kwargs.get('email')
        if not lookup_email or not password:
            return None
        
        try:
            user = User.objects.get(email__iexact=lookup_email)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            User().set_password(password)
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
