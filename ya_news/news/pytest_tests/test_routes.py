from django.urls import reverse
from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def homepage_url():
    return reverse('news:home')


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def news_detail_url(news_sample):
    return reverse('news:detail', args=(news_sample.id,))


@pytest.fixture
def register_url():
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


HOMEPAGE = pytest.lazy_fixture('homepage_url')
REGISTER = pytest.lazy_fixture('register_url')
LOGIN = pytest.lazy_fixture('login_url')
LOGOUT = pytest.lazy_fixture('logout_url')
NEWS_DETAIL = pytest.lazy_fixture('news_detail_url')
EDIT_COMMENT = pytest.lazy_fixture('edit_comment_url')
DELETE_COMMENT = pytest.lazy_fixture('delete_comment_url')

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('url_login', (LOGIN,))
@pytest.mark.parametrize('name', (
    DELETE_COMMENT,
    EDIT_COMMENT,
))
def test_edit_delete_comment_anonymous(client, name, url_login):
    assertRedirects(client.get(name), f'{url_login}?next={name}')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOMEPAGE, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (REGISTER, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (LOGIN, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (LOGOUT, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (NEWS_DETAIL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (DELETE_COMMENT, pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (DELETE_COMMENT, pytest.lazy_fixture('reader_client'),
         HTTPStatus.NOT_FOUND),
        (EDIT_COMMENT, pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (EDIT_COMMENT, pytest.lazy_fixture('reader_client'),
         HTTPStatus.NOT_FOUND)
    )
)
def test_all(url, parametrized_client, expected_status):
    assert parametrized_client.get(url).status_code == expected_status
