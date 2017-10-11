import json

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_jwt import utils


client = Client()
User = get_user_model()


class TestViewTestCase(TestCase):
    
    def setUp(self):
        self.username = 'auth'
        self.email = 'auth@gmail.com'
        self.password = 'passwd'
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.user = User.objects.create_superuser(username=self.username, email=self.email, password=self.password)
        payload = utils.jwt_payload_handler(self.user)
        token = utils.jwt_encode_handler(payload)
        self.auth = 'JWT {}'.format(token)
    
    def test_test(self):
        response = client.get('/api/v1/core/test/', HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, 200)


class CoreTest(TestCase):
    
    def setUp(self):
        self.username = 'auth'
        self.email = 'auth@gmail.com'
        self.password = 'passwd'
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.user = User.objects.create_superuser(username=self.username, email=self.email, password=self.password)
        payload = utils.jwt_payload_handler(self.user)
        token = utils.jwt_encode_handler(payload)
        self.auth = 'JWT {}'.format(token)
        not_admin = User.objects.create_user(username='test1', email='test1@gmail.com')
        payload = utils.jwt_payload_handler(not_admin)
        token = utils.jwt_encode_handler(payload)
        self.not_admin_auth = 'JWT {}'.format(token)
    
    def test_admin_access(self):
        response = client.get('/api/v1/core/worker/', HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.get('/api/v1/core/worker/', HTTP_AUTHORIZATION=self.not_admin_auth)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_worker(self):
        response = client.post('/api/v1/core/worker/', json.dumps({ 'shutdown': ['all'] }), 
                              content_type='application/json', HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    