from datetime import datetime, timedelta

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


# @pytest.fixture
# def sorted_comments(news):
#     comments = Comment.objects.filter(news=news)
#     sorted_comments = comments.order_by('created')
#     return sorted_comments


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


# @pytest.fixture
# def sorted_news():
#     news1 = News.objects.create(
#         title='Новость 1',
#         text='Текст новости 1',
#         date=datetime(2023, 5, 26),
#     )
#     news2 = News.objects.create(
#         title='Новость 2',
#         text='Текст новости 2',
#         date=datetime(2023, 5, 27),
#     )
#     news3 = News.objects.create(
#         title='Новость 3',
#         text='Текст новости 3',
#         date=datetime(2023, 5, 25),
#     )
#     sorted_news = News.objects.order_by('-date')
#     return sorted_news


# @pytest.fixture
# def sorted_comments(author, news):
#     # comment1 = Comment.objects.create(
#     #     text='Комментарий 1',
#     #     author=author,
#     #     news=news,
#     #     created=datetime(2023, 5, 1),
#     # )
#     # comment2 = Comment.objects.create(
#     #     text='Комментарий 2',
#     #     author=author,
#     #     news=news,
#     #     created=datetime(2023, 5, 3),
#     # )
#     # comment3 = Comment.objects.create(
#     #     text='Комментарий 3',
#     #     author=author,
#     #     news=news,
#     #     created=datetime(2023, 5, 2),
#     # )
#     sorted_comments = Comment.objects.filter(news=news).order_by('created')
#     # return sorted_comments
#     return sorted_comments

# @pytest.fixture
# def create_comments(news, author):
#     comments_data = [
#         {'text': 'Средний комментарий', 'days_ago': 2},
#         {'text': 'Новый комментарий', 'days_ago': 1},
#         {'text': 'Старый комментарий', 'days_ago': 3},
#     ]
#
#     comments = []
#     current_date = datetime.now()
#
#     for comment_data in comments_data:
#         created_date = current_date - timedelta(days=comment_data['days_ago'])
#         comment = Comment.objects.create(
#             text=comment_data['text'],
#             author=author,
#             news=news,
#             created=created_date,
#         )
#         comments.append(comment)
#
#     return comments


@pytest.fixture
def comments(author, news):
    now = datetime.now()

    comment1 = Comment.objects.create(
        text='старый Комментарий 1',
        author=author,
        news=news,
        created=now - timedelta(days=3),
    )

    comment2 = Comment.objects.create(
        text='средний Комментарий 2',
        author=author,
        news=news,
        created=now - timedelta(days=2),
    )

    comment3 = Comment.objects.create(
        text='новый Комментарий 3',
        author=author,
        news=news,
        created=now - timedelta(days=1),
    )

    return [comment1, comment2, comment3]


@pytest.fixture
def recent_news(author):
    # current_date = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now()
    recent_news_1 = News.objects.create(
        title='Свежая новость 1',
        text='Текст свежей новости 1',
        date=now,
    )
    recent_news_2 = News.objects.create(
        title='Свежая новость 2',
        text='Текст свежей новости 2',
        date=now - timedelta(days=1),
    )
    recent_news_3 = News.objects.create(
        title='Свежая новость 3',
        text='Текст свежей новости 3',
        date=now - timedelta(days=2),
    )
    return recent_news_3, recent_news_2, recent_news_1
