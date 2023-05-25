from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment

User = get_user_model()


def test_anonymous_user_cannot_post_comment(client, news):
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
    comment_count = Comment.objects.count()
    form_data = {
        'text': 'Новый комментарий',
    }
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comment_count + 1


@pytest.mark.django_db
def test_comment_form_with_bad_words():
    bad_word = 'негодяй'
    form_data = {'text': {bad_word}}
    form = CommentForm(data=form_data)

    assert not form.is_valid()
    assert 'text' in form.errors
    assert form.errors['text'][0] == 'Не ругайтесь!'


@pytest.mark.django_db
def test_edit_own_comment(author_client, comment):
    edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = author_client.get(edit_url)

    assert response.status_code == HTTPStatus.OK

    new_text = 'Измененный комментарий'
    data = {'text': new_text}
    edit_response = author_client.post(edit_url, data=data)

    assert edit_response.status_code == HTTPStatus.FOUND

    edited_comment = Comment.objects.get(pk=comment.pk)
    assert edited_comment.text == new_text


@pytest.mark.django_db
def test_delete_own_comment(author_client, comment):
    assert Comment.objects.filter(pk=comment.pk).exists()

    delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(delete_url)

    assert response.status_code == HTTPStatus.FOUND

    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_authenticated_user_cannot_edit_other_users_comment(author, news):
    user = User.objects.create(username='AnotherUser')
    client = Client()
    client.force_login(user)

    comment = Comment.objects.create(
        text='Комментарий',
        author=author,
        news=news,
    )

    edit_url = reverse('news:edit', args=[comment.pk])
    response = client.get(edit_url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_authenticated_user_cannot_delete_other_users_comment(author, news):
    user = User.objects.create(username='AnotherUser')
    client = Client()
    client.force_login(user)

    comment = Comment.objects.create(
        text='Комментарий',
        author=author,
        news=news,
    )

    delete_url = reverse('news:delete', args=[comment.pk])
    response = client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
