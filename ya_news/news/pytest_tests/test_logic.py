from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse
from http import HTTPStatus

from news.forms import WARNING
from news.models import Comment

import pytest


@pytest.mark.django_db
def test_anonymous_user_can_send_comment(client, form_data_comment, news_id):
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_data_comment)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_registered_user_can_send_comment(
        author_client, author,
        form_data_comment,
        news_id
):
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=form_data_comment)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data_comment['text']
    assert new_comment.author == author


def test_no_post_if_bad_words_present(
        author_client, author,
        news_id,
        forms_data_comment_bad_language
):
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=forms_data_comment_bad_language)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


def test_author_can_edit_own_comments(
        author_client,
        comment_id,
        form_data_comment,
        comment,
        news_id
):
    url = reverse('news:edit', args=comment_id)
    url_for_success = reverse('news:detail', args=news_id)
    response = author_client.post(url, form_data_comment)
    assertRedirects(response, f'{url_for_success}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data_comment['text']


def test_other_user_cant_edit_others_comments(
        reader_client,
        comment_id,
        form_data_comment,
        comment,
):
    url = reverse('news:edit', args=comment_id)
    response = reader_client.post(url, form_data_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_own_comments(
        author_client,
        comment_id,
        comment,
        news_id
):
    url = reverse('news:delete', args=comment_id)
    url_for_success = reverse('news:detail', args=news_id)
    response = author_client.post(url)
    assertRedirects(response, f'{url_for_success}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_others_comments(
        reader_client,
        comment_id,
        comment,
):
    url = reverse('news:delete', args=comment_id)
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
