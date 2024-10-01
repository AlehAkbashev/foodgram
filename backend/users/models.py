from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .const import EMAIL_MAX_LEN, USER_MAX_LEN


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=r"^[\w.@+-]+\Z"),
        ],
    )
    email = models.EmailField(max_length=EMAIL_MAX_LEN, unique=True)
    first_name = models.CharField(max_length=USER_MAX_LEN)
    last_name = models.CharField(max_length=USER_MAX_LEN)
    password = models.CharField(max_length=USER_MAX_LEN)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return str(self.username)
