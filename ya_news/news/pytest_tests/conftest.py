from datetime import datetime, timedelta

from django.test import Client
from django.utils import timezone
import pytest

from news.forms import BAD_WORDS
from news.models import News, Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


bad_words_string = ' '.join(word for word in BAD_WORDS)

# URLS
@pytest.fixture
def homepage_url():
    return reverse('news:home')

# Users and clients
@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


# Instances and their attributes
@pytest.fixture
def news_sample():
    news_sample = News.objects.create(
        title='Новость 1',
        text='Текст новости 1'
    )
    return news_sample


@pytest.fixture
def news_id(news_sample):
    return news_sample.id,


@pytest.fixture
def comment(author, news_sample):
    comment = Comment.objects.create(
        author=author,
        text='Текст комментария тест',
        news=news_sample,
    )
    comment.created = timezone.now() + timedelta(days=1)
    return comment


@pytest.fixture
def comment_id(comment):
    return comment.id,



@pytest.fixture
def multiple_news_samples():
    news_objects = []
    for i in range(
        0 + 1, NEWS_COUNT_ON_HOME_PAGE
        + 1 + 1
    ):
        news_object = News.objects.create(
            title=f'Новость {i}',
            text=f'Текст новости {i}',
            date=datetime.today() - timedelta(days=i),
        ),
        news_objects.append(news_object)
    return news_objects


@pytest.fixture
def multiple_comments(author, news_sample):
    comments = []
    for i in range(222):
        created_at = timezone.now() + timedelta(days=i+1)
        comments.append(
            Comment.objects.create(
                author=author,
                text=f'Текст комментария {i+1}',
                created_at=created_at,
                news=news_sample)
                )
    return comments

#  forms related
@pytest.fixture
def form_data_comment():
    return {
        'text': 'новый текст',
    }


@pytest.fixture
def forms_data_comment_bad_language():
    return {
        'text': f'{bad_words_string}',
    }
