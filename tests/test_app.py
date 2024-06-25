from http import HTTPStatus


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'mensagem': 'Olá, mundo!'}


def test_creat_user(client):
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
