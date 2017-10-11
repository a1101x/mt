from django.test import TestCase
from django.utils import timezone

from apps.userprofile.forms import UserCreationCustomForm


class UserCreationCustomFormTestCase(TestCase):
    """
    Test of custom user creation form.
    """
    def test_valid_form(self):
        """
        Putting valid data in form.
        """
        username = 'testuser'
        email = 'testmail@gmail.com'
        gender = 'M'
        birthday = timezone.now().date()
        data = {
            'username': username,
            'email': email,
            'gender': gender,
            'birthday': birthday
        }
        form = UserCreationCustomForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('username'), username)

    def test_invalid_form(self):
        """
        Putting invalid data in form.
        """
        username = 'testuser'
        email = 'testmail@gmail.com'
        gender = 'M'
        birthday = timezone.now().date()
        data = {
            'username': username,
            'gender': gender,
            'birthday': birthday
        }
        form = UserCreationCustomForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)
