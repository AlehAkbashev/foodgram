import pytest
from django.test import Client
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from recipes.models import Ingredient, Tag

new_user = {
    "email": "new_user@yandex.ru",
    "username": "new_user",
    "first_name": "New",
    "last_name": "User",
    "password": "kolokol_1234",
}

second_user = {
    "email": "vpupkin1@yandex.ru",
    "username": "vasya2.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "kolokol_1234",
}

new_password = {
    "current_password": "kolokol_1234",
    "new_password": "kolobok123",
}

data_for_login = {
    "email": "user@mail.ru",
    "password": "kolokol_1234"
}


@pytest.fixture
def auth_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="AuthUser", email="user@mail.ru", password="kolokol_1234"
    )
    return user


@pytest.fixture
def auth_user_client(auth_user):
    client = Client()
    client.force_login(auth_user)
    return client


@pytest.fixture
def token_for_auth_user(auth_user):
    token, _ = Token.objects.get_or_create(user=auth_user)
    return token


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_user_client(token_for_auth_user, api_client, auth_user):
    api_client.credentials(
        HTTP_AUTHORIZATION="Token " + token_for_auth_user.key
    )
    api_client.login(user=auth_user)
    return api_client


@pytest.fixture
def auth_user_id(auth_user):
    return (auth_user.id,)


@pytest.fixture
def ingredient():
    ingredient = Ingredient.objects.create(
        name="Название ингредиента", measurement_unit="Единица измерения"
    )
    return ingredient


@pytest.fixture
def ingredient_id(ingredient):
    return ingredient.id


@pytest.fixture
def tag():
    tag = Tag.objects.create(name="Название тега", color="aaaa", slug="slug")
    return tag


@pytest.fixture
def tag_id(tag):
    return tag.id
