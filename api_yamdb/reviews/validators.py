import re
from django.utils import timezone
from django.core.exceptions import ValidationError

from api_yamdb.settings import RESERVED_USERNAME, VALID_USERNAME


def validate_year(year):
    if year > timezone.now().year:
        raise ValidationError(f'Год {year} больше текущего!')


def validate_username(username):
    if username.lower() == RESERVED_USERNAME:
        raise ValidationError(f'Имя пользователя не может быть {username}.')
    if not re.search(VALID_USERNAME, username):
        unmatched = re.sub(VALID_USERNAME, '', str(username))
        raise ValidationError(f'Обнаружены недопустимые символы: {unmatched}!')
