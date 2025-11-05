import os
from typing import Optional, Literal
from xmlrpc.client import boolean
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, timezone, datetime
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
from fastapi import Depends, HTTPException, status
from app.core.config import settings
from app.models.user import User
from app.core.db import get_db
from app.api.v1.auth.repository import UserRepository

password_hash = PasswordHash.recommended()
#oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/toek")

#! creamos una excepciones personalizadas

# credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="NO autenticado",headers={"WWW-Authenticate":"Bearer"})


def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="NO autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_expired_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_forbidden():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos suficientes"
    )
def invalid_credentials():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")


# def create_access_token(data:dict,expire_delta:Optional[timedelta]):
#     to_encode=data.copy() #!Copiamos el diccionario

#     # datetime.now(tz=timezone.utc) = 2025-10-21 14:00:00+00:00
#     # timedelta(minutes=30)         = 0:30:00
#     # Resultado final:              2025-10-21 14:30:00+00:00

#     expire=datetime.now(tz=timezone.utc) +( expire_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode["exp"]=expire
#     #to_encode.update({"exp":expire})
#     print(f"create_access_token.toencode:{to_encode}")
#     token=jwt.encode(payload=to_encode,key=settings.JWT_SECRET,algorithm=settings.JWT_ALGORITHM)
#     print(f"create_access_token.token:{token}")
#     return token


def create_access_token(sub: str, minutes: int | None=None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": sub, "exp": expire},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    payload = jwt.decode(
        jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    print(f"token decodificado {payload}")
    return payload


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_schema)
) -> User:

    print(f"get_current_user token: {token}")
    try:
        payload = decode_token(token)  # devuelve un dict
        sub: Optional[str] = payload.get("sub")
        #username: Optional[str] = payload.get("username")
        if not sub: #or not username:
            raise credentials_exception()
        user_id = int(sub)

    except ExpiredSignatureError:
        raise raise_expired_token()
    except InvalidTokenError:
        raise credentials_exception()
    except PyJWTError:
        raise invalid_credentials()
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise invalid_credentials()
    return user


def has_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> boolean:
    return password_hash.verify(plain, hashed)


def require_role(min_role: Literal["user", "editor", "admin"]):
    order = {"user": 0, "editor": 1, "admin": 2}

    def evaluation(user: User = Depends(get_current_user)) -> User:
        if order[user.role] < order[min_role]:
            raise raise_forbidden()
        return user

    return evaluation  # ✅ Devuelves la función para que FastAPI la use después

#! Para construir y mostrar el formulario de oauth2 en openapi
async def auth2_token(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    repository=UserRepository(db)
    user=repository.get_by_email(form.username)
    
    if not user or not verify_password(form.password,user.hashed_password):
        raise invalid_credentials()
    token=create_access_token(sub=str(user.id))
    return {
        "access_token":token,
        "token_type": "bearer"
    }


require_user=require_role("user")
require_editor=require_role("editor")
require_admin=require_role("admin")
