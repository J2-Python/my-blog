#! si no encuentra DATABASE_URL usa sqlite
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase


# load_dotenv() #Para leer el .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")# por defecto usa sqlite
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
print(f"Diccionario:{engine_kwargs}")
test = {**engine_kwargs}
print(test)  # print {"connect_args":{"check_same_thread":False}}
#! future=True permite usar codigo moderno de sqlalchemy 2.0
engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs)
#! El commit es controlado y el autoguardado esta deshabilitado
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)


class Base(DeclarativeBase):
    #! La clase Base ya hereda todos losatributos de DeclarativeBase por eso ponemos el pass
    pass


def get_db():
    db = SessionLocal()
    print(f"tipo db: {type(db)}")
    try:
        yield db
    finally:
        db.close()
