from django.urls import reverse
from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, CommentForm, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

FORM_DATA_COMMENT = {
    'text': 'новый текст',
}


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
    client, url_news_detail, url_login
):
    assertRedirects(
        client.post(url_news_detail, data=FORM_DATA_COMMENT),
        f'{url_login}?next={url_news_detail}'
    )
    assert Comment.objects.count() == 0


@pytest.mark.parametrize('url_news_detail', (NEWS_DETAIL,))
def test_registered_user_can_comment(
        author_client,
        author,
        news_sample,
        url_news_detail
):
    assertRedirects(
        author_client.post(url_news_detail, data=FORM_DATA_COMMENT),
        f'{url_news_detail}#comments'
    )
    assert Comment.objects.count() == 1
    assert (CommentForm(data=FORM_DATA_COMMENT).is_valid()) is True
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA_COMMENT['text']
    assert new_comment.author == author
    assert new_comment.news == news_sample


@pytest.mark.parametrize('url_news_detail', (NEWS_DETAIL,))
def test_no_post_if_bad_words_present(
        author_client,
        url_news_detail
):
    for bad_word in BAD_WORDS:
        assertFormError(
            author_client.post(
                url_news_detail,
                data={'text': f'{bad_word}'}),
            'form', 'text', errors=(WARNING)
        )
        assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'url_edit_comment, url_news_detail',
    [(EDIT_COMMENT, NEWS_DETAIL)]
)
def test_author_can_edit_own_comments(
        author_client,
        comment,
        author,
        news_sample,
        url_edit_comment,
        url_news_detail
):
    assertRedirects(
        author_client.post(url_edit_comment, FORM_DATA_COMMENT),
        f'{url_news_detail}#comments'
    )
    assert Comment.objects.count() == 1
    assert (CommentForm(data=FORM_DATA_COMMENT).is_valid()) is True
    comment.refresh_from_db()
    assert comment.text == FORM_DATA_COMMENT['text']
    assert comment.author == author
    assert comment.news == news_sample


@pytest.mark.parametrize('url_edit_comment', (EDIT_COMMENT,))
def test_other_user_cant_edit_others_comments(
        reader_client,
        comment,
        author,
        news_sample,
        url_edit_comment
):
    assert reader_client.post(
        url_edit_comment, FORM_DATA_COMMENT
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
