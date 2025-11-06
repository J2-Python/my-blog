from app.core.db import Base
from sqlalchemy import Integer,String
from sqlalchemy.orm import Mapped,mapped_column,relationship
class CategoryORM(Base):
    __tablename__="categories"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,index=True)
    name:Mapped[str]=mapped_column(String(60),unique=True,index=True)
    slug:Mapped[str]=mapped_column(String(60),unique=True,index=True)
    #passive_deletes cuando se elimina una categoria confia en el on delete cascade y hace la eliminacion de los registros hijos sin consultarlos previamente
    posts=relationship("PostORM",back_populates="category",cascade="all, delete",passive_deletes=True)