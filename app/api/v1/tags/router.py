from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.tags import repository
from app.api.v1.tags.repository import TagRepository
from app.api.v1.tags.schemas import TagCreate, TagPublic, TagUpdate
from app.core.db import get_db
from app.core.security import (
    get_current_user,
    require_user,
    require_admin,
    require_editor,
)
from app.models import User


router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=dict)
def list_tags(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    order_by: str = Query("id", pattern="^(id|name)$"),
    direction: str = Query("asc", pattern="^(asc|desc)$"),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    repository = TagRepository(db)
    return repository.list_tags(
        page=page,
        per_page=per_page,
        order_by=order_by,
        direction=direction,
        search=search,
    )


@router.post(
    "",
    response_model=TagPublic,
    response_description="Post creado (ok)",
    status_code=status.HTTP_201_CREATED,
)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    # user=Depends(get_current_user)
    _editor: User = Depends(require_editor),
):
    repository = TagRepository(db)
    print(f"Tag create: {type(tag)} value: {tag}")
    try:
        tag_created = repository.create_tag(name=tag.name)
        db.commit()
        db.refresh(tag_created)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear tag")


@router.put("/{tag_id}", response_model=TagPublic)
def update_tag(
    tag_id: int,
    body: TagUpdate,
    db: Session = Depends(get_db),
    # user=Depends(get_current_user)
    _editor: User = Depends(require_editor) # 👉 solo editores pueden actualizar
):
    repository = TagRepository(db)
    tag = repository.get_tag(tag_id)

    if not tag:
        raise HTTPException(status_code=400, detail="Tag no encontrado")
    # body.name
    updates = body.model_dump(
        exclude_none=True
    )  # convertimos el objeto de pydantic a un dict
    tag = repository.update_tag(tag, updates)

    try:
        db.commit()
        db.refresh(tag)
        # return TagPublic.model_validate(tag)
        return tag
    except SQLAlchemyError as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="error al actualizar Tag")


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    # user=Depends(get_current_user),
    _admin: User = Depends(require_admin), # 👉 solo admins pueden eliminar
):
    repository = TagRepository(db)
    tag = repository.get_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=400, detail="Tag no encontrado")
    try:
        repository.delete_tag(tag)
        db.commit()
    except SQLAlchemyError as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al borrar el tag")


@router.get("/popular/top")
def get_most_popular_tag(
    db: Session = Depends(get_db),
    #user=Depends(get_current_user)
    _user=Depends(require_user) # 👉 solo users pueden consultar
    ):
    repository = TagRepository(db)
    row = repository.most_popular()
    if not row:
        raise HTTPException(status_code=404, detail="No hay tags en uso")
    return row
