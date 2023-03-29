from django.contrib.auth.models import AbstractUser
from django.db import models


# USER = 'user'
# MODERATOR = 'moderator'
# ADMIN = 'admin'
# ROLES = (
#     (USER, 'Пользователь'),
#     (MODERATOR, 'Модератор'),
#     (ADMIN, 'Администратор'),
# )



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


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Категория')
    slug = models.SlugField(unique=True, verbose_name='Ссылка_категории')

    class Meta:
        default_related_name = 'category'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Жанр')
    slug = models.SlugField(unique=True, verbose_name='Ссылка_жанра')

    class Meta:
        default_related_name = 'genre'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        Category,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Slug категории',
        help_text='Категория, к которой относится произведение'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Slug жанра',
        help_text='Жарн, к которому относится произведение'
    )
    # DateField ?
    year = models.CharField(max_length=4)

    class Meta:
        default_related_name = 'title'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'], name='title_unique')
        ]

    def __str__(self):
        return self.name
