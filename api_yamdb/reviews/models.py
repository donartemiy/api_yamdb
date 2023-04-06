from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import (LEN_STR, LIMIT_BIO,
                                LIMIT_EMAIL, LIMIT_NAME, LIMIT_ROLE,
                                LIMIT_SLUG, LIMIT_USERNAME,
                                MAX_VALUE, MIN_VALUE, LIMIT_SELFTEXT)
from .validators import validate_username, validate_year

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
USER_RU = 'юзер'
MODERATOR_RU = 'модератор'
ADMIN_RU = 'админ'
ROLES = (
    (USER, USER_RU),
    (MODERATOR, MODERATOR_RU),
    (ADMIN, ADMIN_RU),
)


class User(AbstractUser):
    username = models.CharField(verbose_name='Пользователь',
                                validators=(validate_username,),
                                max_length=LIMIT_USERNAME,
                                unique=True,
                                blank=False,
                                null=False)
    email = models.EmailField(verbose_name='E-Mail',
                              unique=True,
                              max_length=LIMIT_EMAIL,
                              blank=False,
                              null=False)
    bio = models.TextField(verbose_name='О себе',
                           blank=True,
                           max_length=LIMIT_BIO)
    first_name = models.CharField(verbose_name='имя',
                                  max_length=LIMIT_USERNAME,
                                  blank=True)
    last_name = models.CharField(verbose_name='фамилия',
                                 max_length=LIMIT_USERNAME,
                                 blank=True)
    role = models.CharField(verbose_name='Уровень доступа',
                            choices=ROLES,
                            default=USER,
                            blank=True,
                            max_length=LIMIT_ROLE)

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class CommonCategoryGenre(models.Model):
    """ Abstract model for storing common data. """
    name = models.CharField(max_length=LIMIT_NAME)
    slug = models.SlugField(
        max_length=LIMIT_SLUG,
        unique=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name[:LEN_STR]


class Category(CommonCategoryGenre):
    class Meta(CommonCategoryGenre.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CommonCategoryGenre):
    class Meta(CommonCategoryGenre.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=LIMIT_NAME, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        help_text='Категория, к которой относится произведение'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        help_text='Жарн, к которому относится произведение'
    )
    year = models.IntegerField(
        verbose_name='Дата выхода',
        validators=[validate_year],
        db_index=True
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг',
        null=True,
        default=None
    )

    class Meta:
        default_related_name = 'title'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'], name='title_unique')
        ]

    def __str__(self):
        return self.name


class ReviewCommentModel(models.Model):
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[: LIMIT_SELFTEXT]


class Review(ReviewCommentModel):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(MIN_VALUE, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(MAX_VALUE, 'Допустимы значения от 1 до 10')
        ]
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(ReviewCommentModel):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
