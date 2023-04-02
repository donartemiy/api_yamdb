from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_username

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
LIMIT_USERNAME = 150
LIMIT_EMAIL = 254
LIMIT_BIO = 300
LIMIT_ROLE = 50
LIMIT_NAME = 256
LIMIT_SLUG = 50


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


class Category(models.Model):
    name = models.CharField(max_length=LIMIT_NAME, verbose_name='Категория')
    slug = models.SlugField(
        max_length=LIMIT_SLUG,
        unique=True,
        verbose_name='Ссылка категории')

    class Meta:
        default_related_name = 'category'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=LIMIT_NAME, verbose_name='Жанр')
    slug = models.SlugField(
        max_length=LIMIT_SLUG,
        unique=True,
        verbose_name='Ссылка жанра')

    class Meta:
        default_related_name = 'genre'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=LIMIT_NAME, verbose_name='Название')
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
    year = models.CharField(max_length=4)

    class Meta:
        default_related_name = 'title'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'], name='title_unique')
        ]

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['pub_date']
