from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from django.shortcuts import reverse

from news.models import News


@pytest.mark.django_db
def test_news_count_on_homepage(client, news):
    for i in range(11):
        News.objects.create(
            title=f'Заголовок {i}',
            text=f'Новость {i}',
        )

    response = client.get(reverse('news:home'))

    assert response.status_code == HTTPStatus.OK

    assert len(response.context['news_list']) <= 10


@pytest.mark.django_db
def test_news_sorted_by_date(news):
    current_date = datetime.now().date()
    news1 = news
    news2 = News.objects.create(
        title='Заголовок 2',
        text='Новость 2',
        date=current_date - timedelta(days=1),
    )
    news3 = News.objects.create(
        title='Заголовок 3',
        text='Новость 3',
        date=current_date + timedelta(days=1),
    )

    sorted_news = News.objects.order_by('-date')

    assert sorted_news[0] == news3
    assert sorted_news[1] == news1
    assert sorted_news[2] == news2


def test_sorted_comments(sorted_comments):
    previous_comment_date = None
    for comment in sorted_comments:
        if previous_comment_date:
            assert comment.created_at >= previous_comment_date
        previous_comment_date = comment.created_at


def test_comment_form_anonymous_user(client, news):
    name = 'news:detail'
    url = reverse(name, args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


def test_comment_form_authorized_user(admin_client, news):
    name = 'news:detail'
    url = reverse(name, args=(news.pk,))
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
