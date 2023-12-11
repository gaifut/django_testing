from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

LOGIN_URL = 'users:login'
NOTES_DETAIL = 'notes:detail'
NOTES_EDIT = 'notes:edit'
NOTES_DELETE = 'notes:delete'


class TestRoute(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_author, _ = User.objects.get_or_create(username='user author')
        cls.note = Note.objects.create(
            title='Заголовок NEW',
            text='text',
            author=cls.user_author
        )
        cls.user_reader = User.objects.create(username='user reader')

    def test_pages_availability_anonymous_success(self):
        urls = (
            'notes:home',
            'users:signup',
            LOGIN_URL,
            'users:logout',
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_authorised_users(self):
        user_statuses = (
            (self.user_author, HTTPStatus.OK),
            (self.user_reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in (
                NOTES_DETAIL,
                NOTES_EDIT,
                NOTES_DELETE
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse(LOGIN_URL)
        urls = (
            ('notes:list', None),
            (NOTES_DETAIL, (self.note.slug,)),
            (NOTES_EDIT, (self.note.slug,)),
            (NOTES_DELETE, (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)


