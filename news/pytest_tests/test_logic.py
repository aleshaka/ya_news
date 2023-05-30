from http import HTTPStatus

import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from news.forms import WARNING
from news.models import Comment, News

User = get_user_model()


def test_anonymous_user_cannot_post_comment(client, news):
    """
    Проверяет что анонимный пользователь не может отправить комментарий.
    """
    comment_count = Comment.objects.count()
    form_data = {
        'text': 'Новый комментарий',
    }
    url = reverse('news:detail', args=[news.pk])
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comment_count


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(author_client, news):
    """
    Проверяет что авторизованный пользователь может отправить комментарий.
    """
    comment_count = Comment.objects.count()
    form_data = {
        'text': 'Новый комментарий',
        'author': 'Автор'
    }
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comment_count + 1
    comment = Comment.objects.latest('id')
    assert comment.text == form_data['text']
    assert comment.news == news
    assert str(comment.author) == form_data['author']


@pytest.mark.django_db
def test_create_comment_with_bad_words(author_client, news):
    """
    Проверяет комментарий на содержание запрещенных слов
    """
    bad_word = 'по любому ты редиска'
    response = author_client.post(
        reverse('news:detail', args=[news.pk]), {'text': f'Это {bad_word}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0
    assert WARNING.encode() in response.content


@pytest.mark.django_db
def test_edit_own_comment(author_client, comment):
    """
    Проверяет что авторизованный пользователь может edit свои комментарии.
    """
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    new_text = 'Измененный комментарий'
    data = {'text': new_text}
    edit_response = author_client.post(edit_url, data=data)
    assert edit_response.status_code == HTTPStatus.FOUND
    edited_comment = Comment.objects.get(pk=comment.pk)
    assert edited_comment.text == new_text
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author
    assert edited_comment.created == comment.created


@pytest.mark.django_db
def test_delete_own_comment(author_client, comment):
    """
    Проверяет что авторизованный пользователь может delete свои комментарии.
    """
    assert Comment.objects.filter(pk=comment.pk).exists()
    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_authenticated_user_cannot_edit_other_users_comment(
        author, news, client
):
    """
    Проверяет что авторизованный пользователь не может edit чужие комментарии.
    """
    user = User.objects.create(username='AnotherUser')
    client.force_login(user)
    comment = Comment.objects.create(
        text='Комментарий',
        author=author,
        news=news,
    )
    edit_url = reverse('news:edit', args=[comment.pk])
    data = {'text': 'Измененный комментарий'}
    response = client.post(edit_url, data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Комментарий'


@pytest.mark.django_db
def test_authenticated_user_cannot_delete_other_users_comment(
    author, news, client
):
    """
    Проверяет что авторизованный пользователь не может del чужие комментарии.
    """
    user = User.objects.create(username='AnotherUser')
    client.force_login(user)
    comment = Comment.objects.create(
        text='Комментарий',
        author=author,
        news=news,
    )
    initial_post_count = News.objects.count()
    initial_posts = list(News.objects.all())
    delete_url = reverse('news:delete', args=[comment.pk])
    response = client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert News.objects.count() == initial_post_count
    assert list(News.objects.all()) == initial_posts
