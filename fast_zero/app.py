from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get('/ola', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def ola_mundo():
    return """
    <html>
        <head>
            <title>Primeiro olá mundo</title>
        </head>
        <body>
            <h1>Olá, mundo!</h1>
        </body>
    </html>
    """


@app.get('/')
def read_root():
    return {'mensagem': 'Olá, mundo!'}
