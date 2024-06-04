import datetime

from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from schemas import SignUpModel, LoginMadel
from database import session, engine
from sqlalchemy import or_
from models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT

auth_rooter = APIRouter(prefix="/auth")
session = session(bind=engine)


@auth_rooter.get('/')
async def auth(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    return {"massage": "Auth rooter"}


@auth_rooter.get('/signup')
async def signup():
    return {"massage": "Register page"}


@auth_rooter.post('/signup', status_code=status.HTTP_200_OK)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu emaildan oldin ro'yxatdan o'tkazilgan")

    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu username mavjud")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),  # pip install werkzeug | shifirlash uchun
        is_active=user.is_active,
        is_staff=user.is_staff
    )
    session.add(new_user)
    session.commit()
    return user


@auth_rooter.get('/login')
async def login():
    return {"massage": "Login page"}


#
# @auth_rooter.post('/login', status_code=status.HTTP_200_OK)
# async def login(user: LoginMadel, Authorize: AuthJWT = Depends()):
#     # db_user = session.query(User).filter(User.username == user.username).first()
#     db_user = session.query(User).filter(or_(
#         User.username == user.username_or_email,
#         User.email == user.username_or_email
#     )).first()
#     if db_user and check_password_hash(db_user.password, user.password):
#         access_token = Authorize.create_access_token(subject=db_user.username)
#         refresh_token = Authorize.create_refresh_token(subject=db_user.username)
#         token = {
#
#             "access": access_token,
#             "refresh": refresh_token
#         }
#         response = {
#             "success": True,
#             "code": 200,
#             "msg": "User successfully login",
#             "data": token
#         }
#
#         return jsonable_encoder(response)
#     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parol yoki username xato")
#

@auth_rooter.post('/login', status_code=status.HTTP_200_OK)
async def login(user: LoginMadel, Authorize: AuthJWT = Depends()):
    db_user = session.query(User).filter(User.username == user.username).first()
    if db_user and check_password_hash(db_user.password, user.password):
        access_lifetime = datetime.timedelta(minutes=60)
        refresh_lifetime = datetime.timedelta(days=3)
        access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username, expires_time=refresh_lifetime)
        token = {
            "access": access_token,
            "refresh": refresh_token
        }
        response = {
            "success": True,
            "code": 200,
            "msg": "User successfully login",
            "id": db_user.id,
            "data": token
        }

        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parol yoki username xato")


@auth_rooter.get("/me")
async def list():
    users = session.query(User).all()

    context = [{
        "id": user.id,
        "username": user.username,
        "password": user.password,
        "email": user.email,
    }
        for user in users
    ]
    return jsonable_encoder(context)


@auth_rooter.get('/login/refresh')
async def refresh_token(Authorize: AuthJWT = Depends()):
    try:
        access_lifetime = datetime.timedelta(minutes=60)
        Authorize.jwt_refresh_token_required()  # valid acses tokenni talab qiladi
        current_user = Authorize.get_jwt_subject()  # access tokendan usernameni ajratib oladi

        # Databasedan userni filter orqali topamiz
        db_user = session.query(User).filter(User.username == current_user).first()
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User topilmadi ")
        #  access token yaratamiz
        new_access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        response_model = {
            "success": True,
            "code": 200,
            "msg": "New access token created",
            "data": {
                "access_token": new_access_token
            }
        }
        return response_model
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh token")
