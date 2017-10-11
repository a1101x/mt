from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

from apps.userprofile.models import (UserDetail, RegistrationActivationEmail, RegistrationActivationSMS)


User = get_user_model()


class UserTestCase(TestCase):
    """
    Tests for default and for extended user models.
    """
    def setUp(self):
        self.test1 = User.objects.create_user(username='test1', email='test1@gmail.com')
        self.test2 = User.objects.create_user(username='test2', email='test2@gmail.com')

    def test_username(self):
        test1 = User.objects.get(username='test1')
        test2 = User.objects.get(username='test2')
        self.assertEqual(test1.username, 'test1')
        self.assertNotEqual(test1.username, 'abracadabra')
        self.assertEqual(test2.username, 'test2')

    def test_email(self):
        test1 = User.objects.get(email='test1@gmail.com')
        test2 = User.objects.get(email='test2@gmail.com')
        self.assertEqual(test1.email, 'test1@gmail.com')
        self.assertNotEqual(test1.email, 'abracadabra@gmail.com')
        self.assertEqual(test2.email, 'test2@gmail.com')

    def test_user_detail(self):
        detail1 = UserDetail.objects.get(user=self.test1)
        detail2 = UserDetail.objects.get(user=self.test2)
        self.assertEqual(detail1.user, self.test1)
        self.assertEqual(detail2.user, self.test2)
        self.assertNotEqual(detail1.user, self.test2)
        with self.assertRaises(IntegrityError):
           UserDetail.objects.create(user=self.test1)

    def test_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='test1', email='test1@gmail.com')


class RegistrationActivationEmailTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='test1', email='test1@gmail.com')
        self.user2 = User.objects.create_user(username='test2', email='test2@gmail.com')
        self.key1 = RegistrationActivationEmail.objects.create(user=self.user1, activation_key='thisisthekey')
        self.key2 = RegistrationActivationEmail.objects.create(user=self.user2, activation_key='thisisthekey')
    
    def test_key_user(self):
        self.assertEqual(self.key1.user, self.user1)
        self.assertEqual(self.key2.user, self.user2)
        self.assertEqual(self.key1.activation_key, 'thisisthekey')
        self.assertEqual(self.key2.activation_key, 'thisisthekey')
        with self.assertRaises(IntegrityError):
            RegistrationActivationEmail.objects.create(user=self.user1, activation_key='thisisthekey')


class RegistrationActivationSMSTestCase(TestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='test1', email='test1@gmail.com')
        self.user2 = User.objects.create_user(username='test2', email='test2@gmail.com')
        self.key1 = RegistrationActivationSMS.objects.create(user=self.user1, pin_code='thisisthekey')
        self.key2 = RegistrationActivationSMS.objects.create(user=self.user2, pin_code='thisisthekey')
    
    def test_key_user(self):
        self.assertEqual(self.key1.user, self.user1)
        self.assertEqual(self.key2.user, self.user2)
        self.assertEqual(self.key1.pin_code, 'thisisthekey')
        self.assertEqual(self.key2.pin_code, 'thisisthekey')
        with self.assertRaises(IntegrityError):
            RegistrationActivationSMS.objects.create(user=self.user1, pin_code='thisisthekey')
