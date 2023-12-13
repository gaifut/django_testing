from datetime import datetime, timedelta

from django.test import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import News, Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


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
def comment(author, news_sample):
    comment = Comment.objects.create(
        author=author,
        text='Текст комментария тест',
        news=news_sample,
    )
    return comment


@pytest.fixture
def multiple_news_samples():
    news_objects = [News(
        title=f'Новость {i}',
        text=f'Текст новости {i}',
        date=datetime.today() - timedelta(days=i),
    )
        for i in range(
        0 + 1, NEWS_COUNT_ON_HOME_PAGE
        + 1 + 1)
    ]
    News.objects.bulk_create(news_objects)


@pytest.fixture
def multiple_comments(author, news_sample):
    comments = []
    for i in range(222):
        created_at = timezone.now() + timedelta(days=i + 1)
        comments.append(
            Comment.objects.create(
                author=author,
                text=f'Текст комментария {i+1}',
                created_at=created_at,
                news=news_sample)
        )
    return comments
