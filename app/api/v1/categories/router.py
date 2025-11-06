from unicodedata import category
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.categories.repository import CategoryRepository
from app.core.db import get_db
from app.api.v1.categories.schemas import CategoryCreate, CategoryUpdate, CategoryPublic

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryPublic])
def list_categories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    repository=CategoryRepository(db)
    return repository.list_many(skip=skip,limit=limit)


@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    repository=CategoryRepository(db)
    exist=repository.get_by_slug(data.slug)
    if exist:
        raise HTTPException(status_code=400,detail="Slug en uso")
    category=repository.create(name=data.name,slug=data.slug)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryPublic)
def get_category(category_id: int, db: Session = Depends(get_db)):
    repository=CategoryRepository(db)
    category=repository.get(category_id)
    if not category:
        raise HTTPException(status_code=404,detail="Category no existe")
    return CategoryPublic.model_validate(category)
        


@router.put("/{category_id}", response_model=CategoryPublic)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    repository=CategoryRepository(db)
    category=repository.get(category_id)
    if not category:
        raise HTTPException(status_code=404,detail="Category no existe")
    # 👉 data.model_dump(exclude_unset=True) convertimos de un objeto de pydantic a un diccionario sin los campos que no fueron actualizados
    updated=repository.update(category,data.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(updated)
    return CategoryPublic.model_validate(updated)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    repository=CategoryRepository(db)
    category=repository.get(category_id)
    if not category:
        raise HTTPException(status_code=404,detail="Category no existe")
    repository.delete(category)
    db.commit()
    return None