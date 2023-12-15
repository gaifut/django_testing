from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, CommentForm, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA_COMMENT = {
    'text': 'новый текст',
}


NEWS_DETAIL = pytest.lazy_fixture('news_detail_url')
LOGIN = pytest.lazy_fixture('login_url')
EDIT_COMMENT = pytest.lazy_fixture('edit_comment_url')
DELETE_COMMENT = pytest.lazy_fixture('delete_comment_url')


def test_anonymous_user_cant_comment(client, news_detail_url, login_url):
    assertRedirects(
        client.post(news_detail_url, data=FORM_DATA_COMMENT),
        f'{login_url}?next={news_detail_url}'
    )
    assert Comment.objects.count() == 0


def test_registered_user_can_comment(
        author_client,
        author,
        news_sample,
        news_detail_url
):
    assertRedirects(
        author_client.post(news_detail_url, data=FORM_DATA_COMMENT),
        f'{news_detail_url}#comments'
    )
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA_COMMENT['text']
    assert new_comment.author == author
    assert new_comment.news == news_sample


@pytest.mark.parametrize("bad_word", BAD_WORDS)
def test_no_post_if_bad_words_present(
    author_client, news_detail_url, bad_word
):
    assertFormError(
        author_client.post(
            news_detail_url,
            data={'text': f'{bad_word}'}),
        'form', 'text', errors=(WARNING)
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_own_comments(
        author_client,
        comment,
        edit_comment_url,
        news_detail_url
):
    original_comment = Comment.objects.get(id=comment.id)
    assertRedirects(
        author_client.post(edit_comment_url, FORM_DATA_COMMENT),
        f'{news_detail_url}#comments'
    )
    comment_from_db = Comment.objects.get(id=comment.id)
    assert (CommentForm(data=FORM_DATA_COMMENT).is_valid()) is True
    assert comment_from_db.text == FORM_DATA_COMMENT['text']
    assert comment_from_db.author == original_comment.author
    assert comment_from_db.news == original_comment.news


def test_other_user_cant_edit_others_comments(
        reader_client,
        comment,
        author,
        news_sample,
        edit_comment_url
):
    original_comment = Comment.objects.get(id=comment.id)
    assert reader_client.post(
        edit_comment_url, FORM_DATA_COMMENT
    ).status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == original_comment.text
    assert comment_from_db.author == original_comment.author
    assert comment_from_db.news == original_comment.news


def test_author_can_delete_own_comments(
        author_client, delete_comment_url, news_detail_url
):
    assertRedirects(
        author_client.post(delete_comment_url),
        f'{news_detail_url}#comments'
    )
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_others_comments(
        reader_client,
        comment,
        author,
        news_sample,
        delete_comment_url
):
    original_comment = Comment.objects.get(id=comment.id)
    response = reader_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == original_comment.text
    assert comment_from_db.author == original_comment.author
    assert comment_from_db.news == original_comment.news
