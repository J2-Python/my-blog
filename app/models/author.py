from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer,String,DateTime
#from conf import Base,engine
from sqlalchemy.orm import Mapped,mapped_column,relationship
from datetime import datetime
from app.core.db import Base

#! Para evitar las importaciones cruzadas al momento de cargar los modelos de sqlAlchemy
if TYPE_CHECKING:
    from .post import PostORM

class AuthorORM(Base):
    __tablename__="authors"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,index=True)
    name:Mapped[str]=mapped_column(String(100),nullable=False)
    email:Mapped[str]=mapped_column(String(100),unique=True,index=True)
    posts: Mapped[List["PostORM"]]=relationship("PostORM",back_populates="author")
    create_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)