from django.urls import reverse
from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

# Pages and their url references
HOMEPAGE = ('news:home', None)
REGISTER_PAGE = ('users:signup', None)
LOGIN_PAGE = ('users:login', None)
LOGOUT_PAGE = ('users:logout', None)
NEWS_SAMPLE_PAGE = ('news:detail', pytest.lazy_fixture('news_id'))
DELETE_COMMENT_PAGE = ('news:delete', pytest.lazy_fixture('comment_id'))
EDIT_COMMENT_PAGE = ('news:edit', pytest.lazy_fixture('comment_id'))


@pytest.fixture
def login_url():
    return reverse('users:login')


LOGIN = pytest.lazy_fixture('login_url')

pytestmark = pytest.mark.django_db


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
    assert client.get(reverse(name, args=args)).status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize('name, args', (
    DELETE_COMMENT_PAGE,
    EDIT_COMMENT_PAGE,
))
def test_delete_edit_comment_author(
    parametrized_client,
    name,
    args,
    expected_status
):
    assert parametrized_client.get(
        reverse(name, args=args)).status_code == expected_status


@pytest.mark.parametrize('url_login', (LOGIN,))
@pytest.mark.parametrize('name, args', (
    DELETE_COMMENT_PAGE,
    EDIT_COMMENT_PAGE,
))
def test_edit_delete_comment_anonymous(client, name, args, url_login):
    expected_url = f'{url_login}?next={reverse(name, args=args)}'
    response = client.get(reverse(name, args=args))
    assertRedirects(response, expected_url)
