from http import HTTPStatus

import pytest
from django.shortcuts import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """
    Проверка доступа страниц.

    Функция проверяет что главная страница, cтраницы регистрации пользователей,
    входа в учётную запись и выхода из неё доступны анонимным пользователям.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('news:detail',))
def test_pages_detail_availability_for_anonymous_user(client, name, news):
    """
    Проверка что cтраница отдельной новости доступна анонимному пользователю.
    """
    url = reverse(name, args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_comment_edit_and_delete_pages_available_for_author(
    author_client, comment, name
):
    """
    Проверка доступа страницы.

    Функция проверяет что cтраницы удаления и редактирования комментария.
    доступны автору комментария.
    """
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_pages_edit_and_delete_redirection_anonymous_user(client, name, news):
    """
    Проверка перенаправления на страницу авторизации.

    Функция проверяет что при попытке перейти на страницу редактирования или
    удаления комментария анонимный пользователь перенаправляется на страницу
    авторизации.
    """
    url = reverse(name, args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(reverse('users:login'))


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_pages_edit_and_delete_availability_for_auth_user(
    admin_client, name, news
):
    """
    Проверка что возвращается ошибка 404.

    Функция проверяет что авторизованный пользователь не может зайти на
    страницы редактирования или удаления чужих комментариев
    (возвращается ошибка 404).
    """
    url = reverse(name, args=(news.pk,))
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
