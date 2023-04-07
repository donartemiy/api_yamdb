from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import (LEN_STR, LIMIT_BIO,
                                LIMIT_EMAIL, LIMIT_NAME, LIMIT_ROLE,
                                LIMIT_SLUG, LIMIT_USERNAME,
                                MAX_VALUE, MIN_VALUE)
from .validators import validate_username, validate_year

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
USER_RU = 'юзер'
MODERATOR_RU = 'модератор'
ADMIN_RU = 'админ'
# SUPERUSER = 'superuser' TODO
# STAFF = 'staff' TODO
ROLES = (
    (USER, USER_RU),
    (MODERATOR, MODERATOR_RU),
    (ADMIN, ADMIN_RU),
)


class User(AbstractUser):
    username = models.CharField(verbose_name='Пользователь',
                                validators=(validate_username,),
                                max_length=LIMIT_USERNAME,
                                unique=True)
    email = models.EmailField(verbose_name='E-Mail',
                              unique=True,
                              max_length=LIMIT_EMAIL)
    bio = models.TextField(verbose_name='О себе',
                           blank=True,
                           max_length=LIMIT_BIO)
    # Если поля не переопределять, перестанет работать max_length FIXME
    # Или для этих полей перенести max_length в serilizer?
    first_name = models.CharField(max_length=LIMIT_USERNAME,
                                  blank=True)
    last_name = models.CharField(max_length=LIMIT_USERNAME,
                                 blank=True)
    role = models.CharField(verbose_name='Уровень доступа',
                            choices=ROLES,
                            default=USER,
                            max_length=LIMIT_ROLE)

    @property
    def is_admin(self):
        # Пользователя также можно считать админом, если он superuser или staff
        return self.role == ADMIN   # or SUPERUSER or STAFF FIXME

    @property
    def is_moderator(self):     # Метод точно нужен? FIXME
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
        ordering = ('name',)

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

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'
        ordering = ('name',)

    def __str__(self):
        return self.name[:LEN_STR]


class CommonReviewCommentModel(models.Model):
    """ Abstract model for storing common data. """
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
        # Заменил LIMIT_SELFTEXT на LEN_STR, который увеличил с 10 до 20)) TODO
        return self.text[:LEN_STR]


class Review(CommonReviewCommentModel):
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

    class Meta(CommonReviewCommentModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(CommonReviewCommentModel):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta(CommonReviewCommentModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
