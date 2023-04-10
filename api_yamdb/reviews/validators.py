from django.conf import settings
import re
from django.utils import timezone
from django.core.exceptions import ValidationError


def validate_year(year):
    if year > timezone.now().year:
        raise ValidationError(f'Год {year} больше текущего!')


def validate_username(username):
    if username.lower() in settings.RESERVED_USERNAMES:
        raise ValidationError(f'Имя пользователя не может быть {username}.')
    if not re.search(settings.VALID_USERNAME, username):
        unmatched = re.sub(settings.VALID_USERNAME, '', str(username))
        raise ValidationError(f'Обнаружены недопустимые символы: {unmatched}!')
