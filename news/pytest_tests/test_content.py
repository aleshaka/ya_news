from http import HTTPStatus

import pytest

# не смешивай Джанго клиент и пайтест клиент
# (isort их совмещает, может у меня настройки isort ни те)
from django.shortcuts import reverse

from news.models import Comment, News
from yanews import settings


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
    assert len(response.context['news_list']) \
           <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_list_sorted(client, recent_news):
    """
    Проверяет, что новости отсортированы по дате.
    """
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    news_list = response.context['news_list']
    news_list = list(news_list)
    # если не преобразовывать в лист
    # то почему то не работает, там видимо QuerySet
    #  assert <QuerySet [<N...я новость 3>]> == [<News: Свежа...ая новость 3>]
    expected_news_list = list(recent_news)
    expected_news_list.sort(key=lambda x: x.date, reverse=True)
    assert news_list == expected_news_list


@pytest.mark.django_db
def test_comment_list(author_client, news, comments):
    """
    Проверяет, что комментарии отсортированы по дате создания.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    comments_on_page = Comment.objects.filter(news=news)
    assert len(comments_on_page) == len(comments)
    sorted_comments = sorted(comments, key=lambda c: c.created)
    for i in range(len(sorted_comments)):
        assert comments_on_page[i] == sorted_comments[i]


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
