from django.urls import reverse
from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import CommentForm, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


@pytest.fixture
def news_detail_url(news_sample):
    return reverse('news:detail', args=(news_sample.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def edit_comment_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse('news:delete', args=(comment.id,))


NEWS_DETAIL = pytest.lazy_fixture('news_detail_url')
LOGIN = pytest.lazy_fixture('login_url')
EDIT_COMMENT = pytest.lazy_fixture('edit_comment_url')
DELETE_COMMENT = pytest.lazy_fixture('delete_comment_url')


@pytest.mark.parametrize('url_news_detail, url_login', [(NEWS_DETAIL, LOGIN)])
def test_anonymous_user_can_comment(
    client, form_data_comment, url_news_detail, url_login
):
    assertRedirects(
        client.post(url_news_detail, data=form_data_comment),
        f'{url_login}?next={url_news_detail}'
    )
    assert Comment.objects.count() == 0


@pytest.mark.parametrize('url_news_detail', (NEWS_DETAIL,))
def test_registered_user_can_comment(
        author_client,
        author,
        form_data_comment,
        news_sample,
        url_news_detail
):
    response = author_client.post(url_news_detail, data=form_data_comment)
    assertRedirects(response, f'{url_news_detail}#comments')
    assert Comment.objects.count() == 1
    assert (CommentForm(data=form_data_comment).is_valid()) is True
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data_comment['text']
    assert new_comment.author == author
    assert new_comment.news == news_sample


@pytest.mark.parametrize('url_news_detail', (NEWS_DETAIL,))
def test_no_post_if_bad_words_present(
        author_client,
        forms_data_comment_bad_language,
        url_news_detail
):
    assertFormError(
        author_client.post(
            url_news_detail, data=forms_data_comment_bad_language
        ), 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'url_edit_comment, url_news_detail',
    [(EDIT_COMMENT, NEWS_DETAIL)]
)
def test_author_can_edit_own_comments(
        author_client,
        form_data_comment,
        comment,
        author,
        news_sample,
        url_edit_comment,
        url_news_detail
):
    assertRedirects(
        author_client.post(url_edit_comment, form_data_comment),
        f'{url_news_detail}#comments'
    )
    assert Comment.objects.count() == 1
    assert (CommentForm(data=form_data_comment).is_valid()) is True
    comment.refresh_from_db()
    assert comment.text == form_data_comment['text']
    assert comment.author == author
    assert comment.news == news_sample


@pytest.mark.parametrize('url_edit_comment', (EDIT_COMMENT,))
def test_other_user_cant_edit_others_comments(
        reader_client,
        form_data_comment,
        comment,
        author,
        news_sample,
        url_edit_comment
):
    assert reader_client.post(
        url_edit_comment, form_data_comment
    ).status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == author
    assert comment.news == news_sample


@pytest.mark.parametrize(
    'url_delete_comment, url_news_detail',
    [(DELETE_COMMENT, NEWS_DETAIL)]
)
def test_author_can_delete_own_comments(
        author_client, url_delete_comment, url_news_detail
):
    assertRedirects(
        author_client.post(url_delete_comment),
        f'{url_news_detail}#comments'
    )
    assert Comment.objects.count() == 0


@pytest.mark.parametrize('url_delete_comment', (DELETE_COMMENT,))
def test_other_user_cant_delete_others_comments(
        reader_client,
        comment,
        author,
        news_sample,
        url_delete_comment
):
    response = reader_client.post(url_delete_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == author
    assert comment.news == news_sample
