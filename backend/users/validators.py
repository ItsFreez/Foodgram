from django.core.exceptions import ValidationError


def ban_name_me(username):
    if username.lower() == 'me':
        raise ValidationError('Неподходящее имя пользователя.')
    return username
