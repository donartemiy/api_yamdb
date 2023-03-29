from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    username = models.CharField(verbose_name='Пользователь',
                                max_length=150,
                                unique=True,
                                blank=False,
                                null=False)
    email = models.EmailField(verbose_name='E-Mail',
                              unique=True,
                              max_length=254,
                              blank=False,
                              null=False)
    bio = models.TextField(verbose_name='О себе',
                           blank=True,
                           max_length=300)
    first_name = models.CharField(verbose_name='имя',
                                  max_length=150,
                                  blank=True)
    last_name = models.CharField(verbose_name='фамилия',
                                 max_length=150,
                                 blank=True)
    role = models.CharField(verbose_name='Уровень доступа',
                            choices=ROLES,
                            default=USER,
                            blank=True,
                            max_length=50)

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username
