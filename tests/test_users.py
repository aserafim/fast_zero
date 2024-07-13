from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_get_user(client, user):
    response = client.get('/users/1')

    assert response.json() == {
        'id': 1,
        'username': 'teste2',
        'email': 'teste2@test.com',
    }


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
            'username': 'teste3',
            'email': 'teste3@test.com',
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


def test_update_wrong_user(client, other_user, token):
    # import pdb
    # pdb.set_trace()
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'password': 'teste2pass',
            'username': 'testusername2',
            'email': 'test@test.com',
            'id': 1,
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


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


def test_delete_wrong_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


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
