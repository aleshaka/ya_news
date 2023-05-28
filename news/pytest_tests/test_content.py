from http import HTTPStatus

import pytest
# не смешивай Джанго клиент и пайтест клиент
# (isort их совмещает, может у меня настройки isort ни те)

from django.shortcuts import reverse

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_count_on_homepage(client, news):
    """
    Проверяет количество новостей на главной странице.
    """
    for i in range(11):
        News.objects.create(
            title=f'Заголовок {i}',
            text=f'Новость {i}',
        )
    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK
    assert len(response.context['news_list']) <= NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sorted_news(sorted_news, client):
    """
    Проверяет, что новости отсортированы по дате.
    """
    response = client.get(reverse('news:home'))
    assert response.status_code == HTTPStatus.OK
    news_titles = response.context['news_list'].values_list('title', flat=True)
    sorted_titles = sorted_news.values_list('title', flat=True)
    assert list(news_titles) == list(sorted_titles)


@pytest.mark.django_db
def test_sorted_comments(sorted_comments, news, client):
    """
    Проверяет, что комментарии отсортированы по дате создания.
    """
    response = client.get(reverse('news:detail', args=[news.pk]))
    assert response.status_code == HTTPStatus.OK
    comments = Comment.objects.filter(news=news)
    sorted_comments_text = sorted_comments.values_list('text', flat=True)
    comments_text = comments.values_list('text', flat=True)
    assert list(comments_text) == list(sorted_comments_text)


def test_comment_form_anonymous_user(client, news):
    """
    Проверяет форму комментария для неавторизованного пользователя.
    """
    name = 'news:detail'
    url = reverse(name, args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


def test_comment_form_authorized_user(admin_client, news):
    """
    Проверяет форму комментария для авторизованного пользователя.
    """
    name = 'news:detail'
    url = reverse(name, args=(news.pk,))
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
