import json
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from rest_framework.test import APIClient, APITestCase

from users_api.models import (
    CustomUser,
    CustomToken,
)
from users_api.services import authenticate_user


CUR_DIR = os.path.dirname(__file__)


class APITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/api'
        cls.files = f'{CUR_DIR}/fixtures/files'
        cls.api_path = '/api/v1/users/'
        cls.user = CustomUser.objects.create_user(
            email='test@cc.com',
            password='test123',
            # url_hash='fc0ecf9c-4c37-4bb2-8c22-938a1dc65da4',
        )
        cls.token = CustomToken.objects.create(user=cls.user)

    def test_auth_view_post(self):
        path = f'{self.path}/auth_view'
        fixtures = (
            (200, 'valid'),
            (401, 'invalid_email'),
            (401, 'invalid_structure'),
            (401, 'invalid_data'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            response = self.client.post(
                path=f'{self.api_path}auth/',
                data=data,
                format='json',
            )

            status_code = response.status_code

            self.assertEqual(status_code, code, msg=fixture)

    def test_custom_user_view_get(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.get(
            path=self.api_path,
        )

        status_code = response.status_code

        self.assertEqual(status_code, 200)

    def test_custom_user_view_patch(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        path = f'{self.path}/custom_user_view/patch'
        fixtures = (
            (200, 'valid'),
            (400, 'wrong_password'),
            (400, 'invalid_structure'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            avatar_path = data.get('avatar_path')

            if avatar_path is not None:
                with open(f"{self.files}/{avatar_path}", 'rb') as image:
                    data['avatar'] = SimpleUploadedFile(image.name, image.read(), content_type='image/jpeg')

            response = self.client.patch(
                path=self.api_path,
                data=data,
                format='multipart',
            )

            status_code = response.status_code

            self.assertEqual(status_code, code, msg=fixture)

    def test_custom_user_view_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.delete(
            path=self.api_path,
        )

        status_code = response.status_code

        self.assertEqual(status_code, 200)
