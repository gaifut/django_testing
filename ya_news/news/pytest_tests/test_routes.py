import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

# Pages and their url references
HOMEPAGE = ('news:home', None)
REGISTER_PAGE = ('users:signup', None)
LOGIN_PAGE = ('users:login', None)
LOGOUT_PAGE = ('users:logout', None)
NEWS_SAMPLE_PAGE = ('news:detail', pytest.lazy_fixture('news_id'))
DELETE_COMMENT_PAGE = ('news:delete', pytest.lazy_fixture('comment_id'))
EDIT_COMMENT_PAGE = ('news:edit', pytest.lazy_fixture('comment_id'))

edit_delete_page_combo = (
        DELETE_COMMENT_PAGE,
        EDIT_COMMENT_PAGE,
    )

@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        HOMEPAGE,
        REGISTER_PAGE,
        LOGIN_PAGE,
        LOGOUT_PAGE,
        NEWS_SAMPLE_PAGE,
    )
)
def test_pages_availability_to_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize('name, args', edit_delete_page_combo)
def test_delete_edit_comment_author(
    parametrized_client,
    name,
    args,
    expected_status
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name, args', edit_delete_page_combo)
def test_edit_delete_comment_anonymous(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)