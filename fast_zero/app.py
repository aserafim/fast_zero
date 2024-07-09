from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import (
    create_acces_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

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
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
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
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Endpoint que recebe como parâmetro um id correspondente
    a um usuário e atualiza os valores.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail='Not enough permission')

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)

    session.commit()
    session.refresh(current_user)

    return current_user


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint que recebe o id do usuário e remove-o do banco.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail='Not enough permission')

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail='Incorrect email or password'
        )

    access_token = create_acces_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}
