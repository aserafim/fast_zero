from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()


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
def read_users(limit: int = 10, skip=0, session=Depends(get_session)):
    """
    Endpoint que retorna a lista de usuários cadastrados.
    """
    user = session.scalars(select(User).limit(limit).offset(skip))
    return {'users': user}


@app.get('/users/{user_id}', response_model=UserPublic)
def get_user(user_id: int, session=Depends(get_session)):
    """
    Endpoint que recebe como parâmetro um número inteiro
    que representa o id do usuário e retorna esse usuário.
    """
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User not found'
        )

    return db_user


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema, session=Depends(get_session)):
    """
    Endpoint que recebe como parâmetro um id correspondente
    a um usuário e atualiza os valores.
    """
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User not found'
        )

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = user.password

    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int, session=Depends(get_session)):
    """
    Endpoint que recebe o id do usuário e remove-o do banco.
    """
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User not found'
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted'}
