import json

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from rest_framework import status
from rest_framework.test import (APIClient, APITestCase)
from rest_framework_jwt import utils

from apps.userprofile.serializers import (UserProfileSerializer, UserDetailSerializer)
from apps.userprofile.models import (UserDetail, RegistrationActivationEmail)


client = Client()
User = get_user_model()


class UserCurrentProfileDetailTest(APITestCase):
    """
    Tests for:
    GET /api/v1/user/currentuser/
    GET /api/v1/user/userprofile/
    GET PUT /api/v1/user/userprofile/{}/
    GET /api/v1/user/userdetail/
    /api/v1/user/userdetail/{}/
    """

    def setUp(self):
        """
        Create admin user and some base users.
        Get JWT for admin.
        """
        self.username = 'auth'
        self.email = 'auth@gmail.com'
        self.password = 'passwd'
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.user = User.objects.create_superuser(username=self.username, email=self.email, password=self.password)
        payload = utils.jwt_payload_handler(self.user)
        token = utils.jwt_encode_handler(payload)
        self.auth = 'JWT {}'.format(token)
        User.objects.create_user(username='test1', email='test1@gmail.com')
        User.objects.create_user(username='test2', email='test2@gmail.com')

    def test_current_user(self):
        """
        GET /api/v1/user/currentuser/
        with JWT auth
        """
        response = client.get('/api/v1/user/currentuser/', HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(id=self.user.id)
        serializer = UserProfileSerializer(user)
        self.assertEqual(response.data, serializer.data)

    def test_user_profile(self):
        """
        GET /api/v1/user/userprofile/
        GET /api/v1/user/userprofile/{}/
        with JWT auth
        """
        response = client.get('/api/v1/user/userprofile/', HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        users = User.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        self.assertEqual(response.data['results'], serializer.data)

        user = User.objects.get(email='auth@gmail.com')
        response = client.get('/api/v1/user/userprofile/{}/'.format(user.id), HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = UserProfileSerializer(user)
        self.assertEqual(response.data, serializer.data)
    
    def test_user_profile_update(self):
        """
        PUT /api/v1/user/userprofile/{}/
        with JWT auth
        """
        user = User.objects.get(email='auth@gmail.com')
        response = client.put('/api/v1/user/userprofile/{}/'.format(user.id), json.dumps({'first_name': 'first_name'}), 
                              content_type='application/json', HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail(self):
        """
        GET /api/v1/user/userdetail/
        GET /api/v1/user/userdetail/{}/
        with JWT auth
        """
        user_id_1 = User.objects.get(email='test1@gmail.com').id
        user_id_2 = User.objects.get(email='test2@gmail.com').id

        response = client.get('/api/v1/user/userdetail/', HTTP_AUTHORIZATION=self.auth)
        users = UserDetail.objects.all()
        serializer = UserDetailSerializer(users, many=True)
        self.assertEqual(response.data['results'], serializer.data)

        response = client.get('/api/v1/user/userdetail/{}/'.format(user_id_1), HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_detail = UserDetail.objects.get(user_id=user_id_1)
        serializer = UserDetailSerializer(user_detail)
        self.assertEqual(response.data, serializer.data)

        response = client.get('/api/v1/user/userdetail/{}/'.format(user_id_2), HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update(self):
        """
        PUT /api/v1/user/userdetail/{}/
        with JWT auth
        """
        user = User.objects.get(email='test1@gmail.com')
        response = client.put('/api/v1/user/userdetail/{}/'.format(user.id), json.dumps({'gender': 'M'}), 
                              content_type='application/json', HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

class UserRegistrationViewSetTest(APITestCase):
    """
    POST /api/v1/user/registration/ 
    """
    def setUp(self):
        self.data = {
            'username': 'test',
            'email': 'test@gmail.com',
            'gender': 'M',
            'birthday': '1990-01-01',
            'phone': '+380123456789'
        }

    def test_get_put_delete(self):
        """
        Only POST is allowed.
        """
        response = client.get('/api/v1/user/registration/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = client.put('/api/v1/user/registration/', json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = client.delete('/api/v1/user/registration/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post(self):
        """
        Test POST.
        """
        response = client.post('/api/v1/user/registration/', json.dumps(self.data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserLoginTest(APITestCase):
    """
    POST /api/v1/user/send_login_email/
    POST /api/v1/user/login/ 
    """
    def setUp(self):
        self.username = 'test'
        self.email = 'test@gmail.com'
        self.password = 'A12345678'
        self.user = User.objects.create_user(username=self.username, email=self.email,
                                             password=self.password, is_active=True)

    def test_get_put_delete(self):
        """
        Only POST is allowed.
        """
        response = client.get('/api/v1/user/send_login_email/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = client.put('/api/v1/user/send_login_email/', json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = client.delete('/api/v1/user/send_login_email/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = client.get('/api/v1/user/login/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = client.put('/api/v1/user/login/', json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = client.delete('/api/v1/user/login/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
