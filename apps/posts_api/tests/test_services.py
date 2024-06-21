import json
import os

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from posts_api.services import (
    get_posts,
    add,
    get_post,
    detail,
    update,
    remove,
    get_posts_by_pk,
)

CUR_DIR = os.path.dirname(__file__)


User = get_user_model()


class ServicesTest(TestCase):
    fixtures = ['users.json', 'posts.json']

    @classmethod
    def setUpTestData(cls):
        cls.path = f'{CUR_DIR}/fixtures/services'
        cls.files = f'{CUR_DIR}/fixtures/files'
        cls.user = User.objects.get(email='test1@cc.com')

    def test_get_posts(self):
        status_code, response_data = get_posts()

        self.assertEqual(status_code, 200)

    def test_add(self):
        path = f'{self.path}/add'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            image_path = data.pop('image_path', None)

            if image_path is not None:
                with open(f"{self.files}/{image_path}", 'rb') as image:
                    data['image'] = SimpleUploadedFile(
                        name=image.name,
                        content=image.read(),
                        content_type='image/jpeg',
                    )

            status_code, response_data = add(
                user=self.user,
                data=data,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_get_post(self):
        path = f'{self.path}/get_post'
        fixtures = (
            (200, 'valid'),
            (404, 'not_found'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                slug = json.load(file)

            status_code, response_data = get_post(
                slug=slug,
                user=self.user,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_detail(self):
        path = f'{self.path}/get_post'
        fixtures = (
            (200, 'valid'),
            (404, 'not_found'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                slug = json.load(file)

            status_code, response_data = detail(
                slug=slug,
                user=self.user,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_update(self):
        path = f'{self.path}/update'
        fixtures = (
            (200, 'valid'),
            (400, 'invalid_structure'),
            (400, 'required_title'),
            (403, 'forbidden'),
            (404, 'not_found'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                data = json.load(file)

            image_path = data.pop('image_path', None)

            if image_path is not None:
                with open(f"{self.files}/{image_path}", 'rb') as image:
                    data['image'] = SimpleUploadedFile(
                        name=image.name,
                        content=image.read(),
                        content_type='image/jpeg',
                    )

            status_code, response_data = update(
                slug=data.pop('slug', None),
                user=self.user,
                data=data,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_remove(self):
        path = f'{self.path}/remove'
        fixtures = (
            (200, 'valid'),
            (404, 'not_found'),
            (403, 'forbidden'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                slug = json.load(file)

            status_code, response_data = remove(
                slug=slug,
                user=self.user,
            )

            self.assertEqual(status_code, code, msg=fixture)

    def test_get_posts_by_pk(self):
        path = f'{self.path}/get_posts_by_pk'
        fixtures = (
            (200, 'valid'),
            (404, 'not_found'),
        )

        for code, name in fixtures:
            fixture = f'{code}_{name}'

            with open(f'{path}/{fixture}_request.json') as file:
                pk = json.load(file)

            status_code, response_data = get_posts_by_pk(
                pk=pk,
                user=self.user,
            )

            self.assertEqual(status_code, code, msg=fixture)
