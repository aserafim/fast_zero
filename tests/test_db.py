from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(
        username='aserafim',
        email='aserafim@tokio.com',
        password='1234',
    )

    session.add(user)
    session.commit()

    result = session.scalar(
        select(User).where(User.email == 'aserafim@tokio.com')
    )

    assert result.username == 'aserafim'
