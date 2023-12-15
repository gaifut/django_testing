from django.contrib.auth import get_user_model
from http import HTTPStatus

from .shared_test_input import SharedTestInput
from .shared_urls import (
    LOGIN_URL,
    NOTES_DETAIL_URL,
    NOTES_EDIT_URL,
    NOTES_DELETE_URL,
    HOMEPAGE_URL,
    SIGNUP_URL,
    LOGOUT_URL,
    NOTE_LIST_URL
)

User = get_user_model()


class TestRoute(SharedTestInput):

    def test_availability_for_authorised_users(self):
        self.generate_single_note()
        user_statuses = (
            (NOTES_DETAIL_URL, self.client_author, HTTPStatus.OK),
            (NOTES_EDIT_URL, self.client_author, HTTPStatus.OK),
            (NOTES_DELETE_URL, self.client_author, HTTPStatus.OK),
            (NOTES_DETAIL_URL, self.client_another, HTTPStatus.NOT_FOUND),
            (NOTES_EDIT_URL, self.client_another, HTTPStatus.NOT_FOUND),
            (NOTES_DELETE_URL, self.client_another, HTTPStatus.NOT_FOUND),
            (HOMEPAGE_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (LOGOUT_URL, self.client, HTTPStatus.OK),
        )

        for url, param_client, status in user_statuses:
            with self.subTest(url=url, client=param_client, status=status):
                self.assertEqual(param_client.get(url).status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            (NOTE_LIST_URL, f'{LOGIN_URL}?next='),
            (NOTES_DETAIL_URL, f'{LOGIN_URL}?next='),
            (NOTES_EDIT_URL, f'{LOGIN_URL}?next='),
            (NOTES_DELETE_URL, f'{LOGIN_URL}?next=')
        )
        for url, redirect in urls:
            with self.subTest(name=url):
                self.assertRedirects(self.client.get(url), f'{redirect}{url}')
