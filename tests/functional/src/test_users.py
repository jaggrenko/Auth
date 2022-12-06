import json
from http import HTTPStatus


def test_register_user(client, session):
    body = json.dumps({'username': 'user1', 'password': '234'})
    response = client.post(
        '/api/v1/auth/register',
        data=body,
        content_type='application/json',
    )

    assert response.status_code == HTTPStatus.OK


def test_register_existent_user(client, session, create_user):
    create_user('user1', '234')
    body = json.dumps({'username': 'user1', 'password': '234'})
    response = client.post(
        '/api/v1/auth/register',
        data=body,
        content_type='application/json',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_register_empty_username(client, session):
    body = json.dumps({'username': '', 'password': '234'})
    response = client.post(
        '/api/v1/auth/login',
        data=body,
        content_type='application/json',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_register_without_username(client, session):
    body = json.dumps({'password': '234'})
    response = client.post(
        '/api/v1/auth/login',
        data=body,
        content_type='application/json',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_login_user(client, session, create_user):
    create_user('user1', '234')
    body = json.dumps({'username': 'user1', 'password': '234'})
    response = client.post(
        '/api/v1/auth/login',
        data=body,
        content_type='application/json',
    )

    assert response.status_code == HTTPStatus.OK


def test_login_non_existent_user(client, session):
    body = json.dumps({'username': 'user2', 'password': '234'})
    response = client.post(
        '/api/v1/auth/login',
        data=body,
        content_type='application/json',
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_login_empty_user(client, session):
    body = json.dumps({'password': '234'})
    response = client.post(
        '/api/v1/auth/login',
        data=body,
        content_type='application/json',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_login_empty_password(client, session):
    body = json.dumps({'user': 'user1'})
    response = client.post(
        '/api/v1/auth/login',
        data=body,
        content_type='application/json',
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_login_wrong_password(client, session, create_user):
    create_user('user1', '234')
    body = json.dumps({'username': 'user1', 'password': '345'})
    response = client.post(
        '/api/v1/auth/login',
        data=body,
        content_type='application/json',
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_logout(client, session, login_user):
    _, tokens = login_user('user1', '234')
    access_token = tokens['access_token']
    body = json.dumps({})
    response = client.post(
        '/api/v1/auth/logout',
        data=body,
        content_type='application/json',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == HTTPStatus.OK


def test_refresh_token(client, session, login_user):
    _, tokens = login_user('user1', '234')
    refresh_token = tokens['refresh_token']
    body = json.dumps({'username': 'user1', 'password': '234'})
    response = client.post(
        '/api/v1/auth/refresh-token',
        data=body,
        content_type='application/json',
        headers={'Authorization': f'Bearer {refresh_token}'}
    )

    assert response.status_code == HTTPStatus.OK


def test_refresh_token_incorrect(client, session, login_user):
    _, tokens = login_user('user1', '234')
    refresh_token = tokens['refresh_token'] + '345345'
    body = json.dumps({'username': 'user1', 'password': '234'})
    response = client.post(
        '/api/v1/auth/refresh-token',
        data=body,
        content_type='application/json',
        headers={'Authorization': f'Bearer {refresh_token}'}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_change_password(client, session, login_user):
    user, tokens = login_user('user1', '234')
    access_token = tokens['access_token']
    body = json.dumps({'old_password': '234', 'new_password': '345'})
    response = client.patch(
        f'/api/v1/auth/change-password/{user.id}',
        data=body,
        content_type='application/json',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == HTTPStatus.OK


def test_change_password_wrong_password(client, session, login_user):
    user, tokens = login_user('user1', '234')
    access_token = tokens['access_token']
    body = json.dumps({'old_password': '345', 'new_password': '456'})
    response = client.patch(
        f'/api/v1/auth/change-password/{user.id}',
        data=body,
        content_type='application/json',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_change_password_nonexistent_user(client, session, login_user):
    user, tokens = login_user('user1', '234')
    access_token = tokens['access_token']
    body = json.dumps({'old_password': '345', 'new_password': '456'})
    response = client.patch(
        '/api/v1/auth/change-password/789',
        data=body,
        content_type='application/json',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
