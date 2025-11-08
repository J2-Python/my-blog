from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from contextlib import contextmanager
from pwdlib import PasswordHash
from app.models import User, CategoryORM, TagORM
from app.seeds.data.users import USERS
from app.seeds.data.categories import CATEGORIES
from app.seeds.data.tags import TAGS
from app.core.db import SessionLocal

def hash_password(plain: str) -> str:
    return PasswordHash.recommended().hash(plain)


@contextmanager
def atomic(db: Session,model_name:str):
    try:
        yield f"🟩 Migrate {model_name}"
        db.commit()
    except Exception:
        db.rollback()
        raise


def _user_by_email(db: Session, email: str) -> Optional[User]:
    return db.execute(select(User).where(User.email == email)).scalars().first()


def _category_by_slug(db: Session, slug: str) -> Optional[CategoryORM]:
    return (
        db.execute(select(CategoryORM).where(CategoryORM.slug == slug))
        .scalars()
        .first()
    )


def _tag_by_name(db: Session, name: str) -> Optional[TagORM]:
    return db.execute(select(TagORM).where(TagORM.name == name)).scalars().first()

#! Idempotente: si se ejecuta varias veces el seed incluso por accidente no se repiten registros, en caso de que existan se sobreescriben y si no existe se crean como nuevo
def seed_user(db: Session) -> None:
    #!atomic() se encargara de hacer el commit() o el roolback()
    with atomic(db,"User") as migrate:
        print(migrate)
        for user in USERS:
            obj = _user_by_email(db, user["email"])
            if obj:
                changed = False
                if obj.full_name != user["full_name"]:
                    obj.full_name = user["full_name"]
                    changed = True
                if user["password"]:
                    obj.hashed_password = hash_password(user["password"])
                    changed = True
                if user["role"]:
                    obj.role = user["role"]  # type: ignore
                if changed:
                    db.add(obj)
            else:
                db.add(
                    User(
                        email=user["email"],
                        full_name=user["full_name"],
                        role=user["role"],
                        hashed_password=hash_password(user["password"]),
                    )
                )
                
def seed_categories(db:Session)->None:
    #!atomic() se encargara de hacer el commit() o el roolback()
    with atomic(db,"Category") as migrate:
        print(migrate)
        for categorie in CATEGORIES:
            obj=_category_by_slug(db,categorie["slug"])
            if obj:
                if obj.name!=categorie["name"]:
                    obj.name=categorie["name"]
                    db.add(obj)
            else:
                db.add(CategoryORM(name=categorie["name"],slug=categorie["slug"]))

def seed_tags(db:Session)->None:
    #!atomic() se encargara de hacer el commit() o el roolback()
    with atomic(db,"Tag") as migrate:
        print(migrate)
        for tag in TAGS:
            obj=_tag_by_name(db,tag["name"])
            if obj:
                if obj.name!=tag["name"]:
                    obj.name=tag["name"]
                    db.add(obj)
            else:
                db.add(TagORM(name=tag["name"]))
            


def run_all()->None:
    with SessionLocal() as db:
        seed_user(db)
        seed_categories(db)
        seed_tags(db)
        

def run_users()->None:
    with SessionLocal() as db:
        seed_user(db)
def run_categories()->None:
    with SessionLocal() as db:
        seed_categories(db)
def run_tags()->None:
    with SessionLocal() as db:
        seed_tags(db)