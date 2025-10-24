import os
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta,timezone,datetime
import jwt
from jwt.exceptions import ExpiredSignatureError,InvalidTokenError
from fastapi import Depends, HTTPException,status
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

#! creamos una excepciones personalizadas

# credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="NO autenticado",headers={"WWW-Authenticate":"Bearer"})

def credentials_exception():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="NO autenticado",headers={"WWW-Authenticate":"Bearer"})


def raise_expired_token():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token expirado",headers={"WWW-Authenticate":"Bearer"})

def raise_forbidden():
    HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="No tienes permisos suficientes")

    

def create_access_token(data:dict,expire_delta:Optional[timedelta]):
    to_encode=data.copy() #!Copiamos el diccionario
    
    # datetime.now(tz=timezone.utc) = 2025-10-21 14:00:00+00:00
    # timedelta(minutes=30)         = 0:30:00
    # Resultado final:              2025-10-21 14:30:00+00:00

    expire=datetime.now(tz=timezone.utc) +( expire_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"]=expire
    #to_encode.update({"exp":expire})
    print(f"create_access_token.toencode:{to_encode}")
    token=jwt.encode(payload=to_encode,key=SECRET_KEY,algorithm=ALGORITHM)
    print(f"create_access_token.token:{token}")
    return token

def decode_token(token:str)->dict:
    payload=jwt.decode(jwt=token,key=SECRET_KEY,algorithms=[ALGORITHM])
    print(f"token decodificado {payload}")
    return payload

async def get_current_user(token:str=Depends(oauth2_schema)):
    
    print(f"get_current_user token: {token}")
    try:
        payload=decode_token(token)# devuelve un dict
        sub:Optional[str]=payload.get("sub")
        username:Optional[str]=payload.get("username")
        if not sub or not username:
            raise credentials_exception()
        
        return {"email":sub,"username":username}
    except ExpiredSignatureError:
        raise raise_expired_token()
    except InvalidTokenError:
        raise credentials_exception()
        