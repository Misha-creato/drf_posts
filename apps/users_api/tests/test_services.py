import json
import os

from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase

from unittest.mock import patch

from users_api.models import (
    CustomUser,
    CustomToken,
)
from users_api.services import (
    auth,
    register,
    detail,
    update,
    retrieve,
    confirm,
    reset,
    reset_request,
    get_user_by,
)


CUR_DIR = os.path.dirname(__file__)


class ServicesTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/services'
        cls.files = f'{CUR_DIR}/fixtures/files'
        cls.user = CustomUser.objects.create_user(
            email='test@cc.com',
            password='test123',
            url_hash='fc0ecf9c-4c37-4bb2-8c22-938a1dc65da4',
        )
        cls.token = CustomToken.objects.create(user=cls.user)

    @patch('users_api.services.send_email_by_type')
    def test_register(self, mock_send_email_by_type):
        mock_send_email_by_type.return_value = 200
        path = f'{self.path}/register'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid_email'),
            (400, 'invalid_structure'),
            (400, 'already_exists'),
            (400, 'password_mismatch'),
        )

        request = self.client.post('/').wsgi_request
        abs_url_func = request.build_absolute_uri

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = register(
                data=data,
                abs_url_func=abs_url_func,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_auth(self):
        path = f'{self.path}/auth'
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

            status_code, response_data = auth(
                data=data,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_detail(self):
        status_code, response_data = detail(
            user=self.user,
        )

        self.assertEqual(status_code, 200)

    def test_update(self):
        path = f'{self.path}/update'
        fixtures = (
            (200, 'valid'),
            (400, 'wrong_password'),
            (400, 'invalid_structure'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            avatar_path = data.pop('avatar_path', None)

            if avatar_path is not None:
                with open(f"{self.files}/{avatar_path}", 'rb') as image:
                    data['avatar'] = SimpleUploadedFile(
                        name=image.name,
                        content=image.read(),
                        content_type='image/jpeg',
                    )

            status_code, response_data = update(
                user=self.user,
                data=data,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_retrieve(self):
        status_code, response_data = retrieve(
            user=self.user,
        )

        self.assertEqual(status_code, 200)

    def test_confirm(self):
        path = f'{self.path}/confirm'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                url_hash = json.load(file)

            status_code, response_data = confirm(
                url_hash=url_hash,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_reset(self):
        path = f'{self.path}/reset'
        fixtures = (
            (400, 'wrong_password'),
            (400, 'invalid'),
            (200, 'valid'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            url_hash = data.pop('url_hash')
            status_code, response_data = reset(
                url_hash=url_hash,
                data=data,
            )

            self.assertEqual(status_code, code, msg=fixture)

    @patch('users_api.services.send_email_by_type')
    def test_reset_request(self, mock_send_email_by_type):
        mock_send_email_by_type.return_value = 200
        path = f'{self.path}/reset_request'
        fixtures = (
            (200, 'valid'),
            (400, 'wrong_email'),
            (400, 'invalid_email'),
            (400, 'invalid'),
        )

        request = self.client.post('/').wsgi_request
        abs_url_func = request.build_absolute_uri

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = reset_request(
                data=data,
                abs_url_func=abs_url_func,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_get_user_by(self):
        path = f'{self.path}/get_user_by'
        fixtures = (
            (200, 'valid'),
            (400, 'not_found'),
            (500, 'invalid'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            status_code, response_data = get_user_by(
                **data
            )

            self.assertEqual(status_code, code, msg=fixture)