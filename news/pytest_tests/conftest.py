from datetime import datetime

import pytest

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    current_date = datetime.now().strftime('%Y-%m-%d')
    news = News.objects.create(
        title='Заголовок',
        text='Новость',
        date=(current_date),
    )
    return news


@pytest.fixture
def sorted_comments(news):
    comments = Comment.objects.filter(news=news)
    sorted_comments = comments.order_by('created')
    return sorted_comments


@pytest.fixture
def slug_for_args(news):
    return (news.slug,)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Комментарий',
        author=author,
        news=news,
    )
    return comment
