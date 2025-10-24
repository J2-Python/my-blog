from pydantic import BaseModel,ConfigDict
from typing import Optional
class Token(BaseModel):
    access_token:str
    token_type:str="bearer"

class TokenData(BaseModel):
    sub:str
    username:str

class UserPublic(BaseModel):
    email:str
    username:str
    model_config=ConfigDict(from_attributes=True)#para que tambien recibe objetos ORM