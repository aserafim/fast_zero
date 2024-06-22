from http import HTTPStatus

from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from fast_zero.app import app


def test_hello_world_deve_retornar_ola_mundo():
    client = TestClient(app)  # Arrange

    response = client.get('/ola')  # Act

    soup = BeautifulSoup(response, 'html.parser')

    h1 = soup.find('h1')

    assert response.status_code == HTTPStatus.OK
    assert h1.text == 'Olá, mundo!', f'H1 errado: {h1.text}'
