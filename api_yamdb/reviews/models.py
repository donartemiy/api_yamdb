from django.contrib.auth.models import AbstractUser
from django.db import models


USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)



# class User(AbstractUser):
#     username = models.CharField(verbose_name='Пользователь',
#                                 max_length=150,
#                                 unique=True,
#                                 blank=False,
#                                 null=False)
#     email = models.EmailField(verbose_name='E-Mail',
#                               unique=True,
#                               max_length=254,
#                               blank=False,
#                               null=False)
#     bio = models.TextField(verbose_name='О себе',
#                            blank=True,
#                            max_length=300)
#     first_name = models.CharField(verbose_name='имя',
#                                   max_length=150,
#                                   blank=True)
#     last_name = models.CharField(verbose_name='фамилия',
#                                  max_length=150,
#                                  blank=True)
#     role = models.CharField(verbose_name='Уровень доступа',
#                             choices=ROLES,
#                             default=USER,
#                             blank=True,
#                             max_length=50)

#     @property
#     def is_user(self):
#         return self.role == USER

#     @property
#     def is_admin(self):
#         return self.role == ADMIN

#     @property
#     def is_moderator(self):
#         return self.role == MODERATOR

#     def __str__(self):
#         return self.username

from django.contrib.auth import get_user_model
User = get_user_model()


class Categories(models.Model):
    name = models.CharField(max_length=256, verbose_name='Категория')
    slug = models.SlugField(unique=True, verbose_name='Ссылка_категории')

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=256, verbose_name='Жанр')
    slug = models.SlugField(unique=True, verbose_name='Ссылка_жанра')

    def __str__(self):
        return self.name


class Reviews(models.Model):
    pass


class Titles(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    # author = models.ForeignKey(
    #     User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(
        Categories,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Slug категории',
        help_text='Категория, к которой относится произведение'
    )
    genre = models.ForeignKey(      # Тут похоже нужно many to many делать?
        # Если вручную создавать промежуточную таблицу, то нужно испольховать
        # ManyToManyField.through
        Genres,
        blank=True,     # Возомжно это нужно убрать, т.к. жанр не обязателен вроде как ?
        null=True,      # Это поле связано с БД, а blank только с проверкой
        on_delete=models.SET_NULL,
        verbose_name='Slug жанра',
        help_text='Жарн, к которому относится произведение'
    )
    year = models.DateTimeField(verbose_name='Год выпуска')
    reviews = models.ForeignKey(
        Reviews,
        blank=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    # related_name добавить ?
