from __future__ import annotations
from typing import List, TYPE_CHECKING
from typing import List, Optional
from sqlalchemy import Integer,String
#from conf import Base,engine
from sqlalchemy.orm import Mapped,mapped_column,relationship
from datetime import datetime
from app.core.db import Base
#! Para evitar las importaciones cruzadas al momento de cargar los modelos de sqlAlchemy
if TYPE_CHECKING:
    from .post import PostORM
class TagORM(Base):
    __tablename__="tags"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,index=True)
    name:Mapped[str]=mapped_column(String(30),unique=True,index=True)
    posts:Mapped[List["PostORM"]]=relationship(secondary="post_tags",back_populates="tags",lazy="selectin")