from http import HTTPStatus

import pytest
from django.urls import reverse

from .conftest import second_user, new_password, new_user, data_for_login
from pytest import lazy_fixture

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    "endpoint, req_method, content, args, status",
    (
        ("api:users-detail", "get", None, pytest.lazy_fixture("auth_user_id"), HTTPStatus.OK),
        ("api:users-list", "get", None, None, HTTPStatus.OK),
        ("api:users-me", "get", None, None, HTTPStatus.OK),
        ("api:users-set-password", "post", new_password, None, HTTPStatus.NO_CONTENT)
    )
)
def test_users_endpoint_for_auth_user(
    endpoint, req_method, content, status, api_user_client, args
):
    url = reverse(endpoint, args=args)
    if req_method == "get":
        response = api_user_client.get(url)
    else:
        response = api_user_client.post(url, data=content, format="json")
    assert response.status_code == status


@pytest.mark.parametrize(
    "endpoint, req_method, content, arg, status",
    (
        ("api:users-detail", "get", None, pytest.lazy_fixture("auth_user_id"), HTTPStatus.OK),
        ("api:users-list", "get", None, None, HTTPStatus.OK),
        ("api:users-list", "post", new_user, None, HTTPStatus.CREATED),
        ("api:users-me", "get", None, None, HTTPStatus.UNAUTHORIZED),
        ("api:users-set-password", "post", new_password, None, HTTPStatus.UNAUTHORIZED)
    )
)
def test_users_endpoint_for_anon_user(
    endpoint, req_method, content, arg, status, api_client
):
    url = reverse(endpoint, args=arg)
    if req_method == "get":
        response = api_client.get(url)
    else:
        response = api_client.post(url, data=content, format="json")
    assert response.status_code == status


@pytest.mark.parametrize(
    "user, status",
    (
        (lazy_fixture("api_client"), HTTPStatus.OK),
        (lazy_fixture("api_user_client"), HTTPStatus.OK)
    )
)
def test_login_endpoint_avalibility(
    user, status, auth_user
):
    response = user.post("/api/auth/token/login", data=data_for_login, format="json")
    assert response.status_code == status


@pytest.mark.parametrize(
    "user, token, status",
    (
        (lazy_fixture("api_client"), None, HTTPStatus.UNAUTHORIZED),
        (lazy_fixture("api_user_client"), lazy_fixture("token_for_auth_user"), HTTPStatus.NO_CONTENT)
    )
)
def test_logout_endpoint_avalibility(
    user, status, token
):
    if token:
        token = token.key
    response = user.post("/api/auth/token/logout", data=token, format="json")
    assert response.status_code == status


@pytest.mark.parametrize(
    "user, status",
    (
        (pytest.lazy_fixture("auth_user_client"), HTTPStatus.NO_CONTENT),
        (pytest.lazy_fixture("client"), HTTPStatus.UNAUTHORIZED),
    ),
)
def test_users_set_password_available(
    user, status, api_client, token_for_auth_user, auth_user_client, auth_user
):
    url = reverse("api:users-set-password")
    if user == auth_user_client:
        api_client.credentials(
            HTTP_AUTHORIZATION="Token " + token_for_auth_user.key
        )
        api_client.login(user=auth_user)
        response = api_client.post(url, data=new_password, format="json")
    else:
        response = user.post(url, data=new_password, format="json")
    assert response.status_code == status
