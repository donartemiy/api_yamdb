import re
from django.utils import timezone
from django.core.exceptions import ValidationError


def validate_year(year):
    if year > timezone.now().year:
        raise ValidationError(f'Год {year} больше текущего!')


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )
    if re.search(r'^[-a-zA-Z0-9_]+$', value) is None:
        raise ValidationError(
            ('Не допустимые символы '), params={'value': value},)
