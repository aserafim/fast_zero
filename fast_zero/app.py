from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

database = []


@app.get('/ola', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def ola_mundo():
    """
    Um endpoint "Olá Mundo" com retorno em HTML
    """
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
    """
    Endpoint raiz retornando "Olá Mundo"
    """
    return {'mensagem': 'Olá, mundo!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    """
    Endpoint que cria um novo usuário e cadastra no banco.
    """
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail='Usuário já existe'
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail='Email já existe'
            )

    db_user = User(
        username=user.username, email=user.email, password=user.password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', response_model=UserList)
def read_users(session=Depends(get_session)):
    """
    Endpoint que retorna a lista de usuários cadastrados.
    """
    user = session.scalars(
        select(User)
    )
    return {'users': user}


@app.get('/users/{user_id}', response_model=UserPublic)
def get_user(user_id: int):
    """
    Endpoint que recebe como parâmetro um número inteiro
    que representa o id do usuário e retorna esse usuário.
    """
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_with_id = database[user_id - 1]

    return user_with_id


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    """
    Endpoint que recebe como parâmetro um id correspondente
    a um usuário e atualiza os valores.
    """
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_with_id = UserDB(id=user_id, **user.model_dump())

    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int):
    """
    Endpoint que recebe o id do usuário e remove-o do banco.
    """
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    del database[user_id - 1]

    return {'message': 'Usuário removido'}
