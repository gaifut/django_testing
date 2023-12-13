from django.urls import reverse
import pytest

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

pytestmark = pytest.mark.django_db


@pytest.fixture
def homepage_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news_sample):
    return reverse('news:detail', args=(news_sample.id,))


HOMEPAGE = pytest.lazy_fixture('homepage_url')
NEWS_DETAIL = pytest.lazy_fixture('news_detail_url')


@pytest.mark.parametrize('url_homepage', (HOMEPAGE,))
def test_news_per_page(client, multiple_news_samples, url_homepage):
    assert (
        client.get(url_homepage).context['object_list'].count()
        == NEWS_COUNT_ON_HOME_PAGE
    )


@pytest.mark.parametrize('url_homepage', (HOMEPAGE,))
def test_news_order(client, url_homepage):
    object_list = client.get(url_homepage).context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.parametrize('url_news_detail', (NEWS_DETAIL,))
def test_comments_order(client, url_news_detail):
    all_comments = client.get(
        url_news_detail).context['news'].comment_set.all()
    for i in range((all_comments).count() - 1):
        assert all_comments[i].created < all_comments[i + 1].created


@pytest.mark.parametrize('url_news_detail', (NEWS_DETAIL,))
def test_anonymous_client_has_no_form(client, url_news_detail):
    assert 'form' not in client.get(url_news_detail).context


@pytest.mark.parametrize('url_news_detail', (NEWS_DETAIL,))
def test_authorized_client_has_form(author_client, url_news_detail):
    assert 'form' in author_client.get(url_news_detail).context
    assert isinstance(
        author_client.get(url_news_detail).context['form'], CommentForm
    )
