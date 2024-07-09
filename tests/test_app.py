from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'mensagem': 'Olá, mundo!'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'Teste1',
            'email': 'teste1@teste.com',
            'password': 'teste1pass',
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        'username': 'Teste1',
        'email': 'teste1@teste.com',
        'id': 1,
    }


def test_create_user_ja_existe(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'User Teste',
            'email': 'teste@teste.com',
            'password': 'teste1pass',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Usuário já existe'}


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    # Precisamos converter o user do
    # sqlAlchemy no user do pydantic para
    # realizar a comparação
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    # import pdb
    # pdb.set_trace()
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'password': 'teste2pass',
            'username': 'testusername2',
            'email': 'test@test.com',
            'id': 1,
        },
    )

    assert response.json() == {
        'username': 'testusername2',
        'email': 'test@test.com',
        'id': 1,
    }


def test_get_user(client, user):
    response = client.get('/users/1')

    assert response.json() == {
        'id': 1,
        'username': 'User Teste',
        'email': 'test@test.com',
    }


def test_get_user_not_found(client):
    response = client.get('/users/100')

    assert response.json() == {'detail': 'User not found'}


"""
Por hora o teste nao faz sentido
pois so o proprio usuario logado
pode atualizar seus dados

def test_update_not_found(client):
    response = client.put(
        '/users/100',
        json={
            'password': 'teste2pass',
            'username': 'aserafim1',
            'email': 'teste@teste.com',
            'id': 100,
        },
    )

    assert response.json() == {'detail': 'User not found'}
"""


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


"""
Por hora o teste nao faz sentido
pois so o proprio usuario logado
pode deletar sua conta

def test_delete_not_found(client: TestClient, token):
    response = client.delete(
        '/users/100', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'detail': 'User not found'}
"""


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token
