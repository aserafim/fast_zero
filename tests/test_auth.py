from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_token_expired_after_time(client, user):
    with freeze_time('2023-07-14 12:00:00'):
        # Gera o token às 12h00
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.ACCEPTED
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):

        # Usa o token às 12h31
        response = client.put(
            f'/users/{user.id}',
            headers={'Authentication': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrogn.com',
                'password': 'wrong',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
