from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from fast_zero.app import app


def test_hello_world_deve_retornar_primeiro_ola_mundo_no_title():
    client = TestClient(app)

    response = client.get('/ola')

    soup = BeautifulSoup(response, 'html.parser')

    title = soup.find('title')

    assert title.text == 'Primeiro olá mundo'
