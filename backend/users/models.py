from django.contrib.auth.models import AbstractUser
from django.db import models

NAME_LEN = 150
MAIL_LEN = 254
PASS_LEN = 150


class CustomUser(AbstractUser):
    """Кастомная модель для пользователя"""

    email = models.EmailField(
        'Электронная почта',
        help_text='Введите адрес электронной почты',
        max_length=MAIL_LEN,
        unique=True,
        blank=False,
        null=False
    )
    username = models.CharField(
        'Имя пользователя',
        help_text='Введите логин',
        max_length=NAME_LEN,
        unique=True,
        blank=False,
        null=False
    )
    first_name = models.CharField(
        'Имя',
        help_text='Введите имя пользователя',
        max_length=NAME_LEN,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        help_text='Введите фамилию пользователя',
        max_length=NAME_LEN,
        blank=False,
        null=False,
    )
    password = models.CharField(
        'Пароль',
        help_text='Введите пароль',
        max_length=PASS_LEN,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower'
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'following'], name='unique_following'
        )]

    def __str__(self):
        return f'Подписка {self.user} на {self.following}'
