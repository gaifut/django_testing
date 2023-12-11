from datetime import datetime, timedelta
from django.utils import timezone
import pytest

from news.forms import BAD_WORDS
from news.models import News, Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

sample_count = 1  # Новость 1 is already reserved and exclided from range
extra_samples_to_exceed_page_limit = 1
today = datetime.today()
now = timezone.now()
bad_words_string = ' '.join(word for word in BAD_WORDS)


# Users and clients
@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, client):
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
    comment.created = now + timedelta(days=1)
    return comment


@pytest.fixture
def comment_id(comment):
    return comment.id,


@pytest.fixture
def comment_two(author, news_sample):
    comment = Comment.objects.create(
        author=author,
        text='Текст комментария 2 тест',
        news=news_sample,
    )
    comment.created = now + timedelta(days=2)
    return comment


@pytest.fixture
def multiple_news_samples():
    news_objects = []
    for i in range(
        0 + sample_count, NEWS_COUNT_ON_HOME_PAGE
        + sample_count + extra_samples_to_exceed_page_limit
    ):
        news_object = News.objects.create(
            title=f'Новость {i}',
            text=f'Текст новости {i}',
            date=today - timedelta(days=i),
        ),
        news_objects.append(news_object)
    return news_objects


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
