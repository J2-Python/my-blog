from fastapi import APIRouter, Depends, HTTPException, status
from .schema import Token, UserPublic
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from app.core.security import create_access_token, decode_token, get_current_user
from datetime import timedelta

FAKE_USERS = {
    "ricardo@example.com": {
        "email": "ricardo@example.com",
        "username": "ricardo",
        "password": "secret123",
    },
    "alumno@example.com": {
        "email": "alumno@example.com",
        "username": "alumno",
        "password": "123456",
    },
    "juan@gmail.com": {
        "email": "juan@gmail.com",
        "username": "alumno",
        "password": "123456",
    },
}

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"form_data {form_data}")
    user = FAKE_USERS.get(form_data.username)  # type: ignore
    print(f"user {user}")
    if not user or user["password"] != form_data.password:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales Invalidas"
        )

    token = create_access_token(
        {"sub": user["email"], "username": user["username"]},
        expire_delta=timedelta(minutes=30),
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me",response_model=UserPublic)
#! este endpoint ya esta protegido y para acceder es necesario un token activo. La validacion ya depende del metodo get_current_user
async def read_me(current=Depends(get_current_user)):
    return {"email":current["email"],"username":current["username"]}
    