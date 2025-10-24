import math
from sqlalchemy.orm import Session
from typing import Annotated, List, Literal, Optional, Union
from fastapi import APIRouter, Depends, File, HTTPException, Path, Query,status,UploadFile
from app.core.db import get_db #Importamos el metodo
from .schemas import PostNotFound, PostPublic,PaginatedPostAdvance,PostCreate,PostUpdate,PostSummary #Importamos las clases
from .repository import PostRepository #Importamos las clases
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.core.security import oauth2_schema,get_current_user
import time
import asyncio
import threading
from app.services.file_storage import save_uploaded_image
router=APIRouter(prefix="/posts",tags=['posts'])#tags no va ayudar en la documentacion y que quede agrupado

@router.get("/sync")
def sync_endpoint():
    print("Sync theread: ",threading.current_thread().name)
    time.sleep(8)
    
    return {"message":"Funcion Sync terminada"}

@router.get("/async")
async def async_endpoint():
    print("Async theread: ",threading.current_thread().name)
    await asyncio.sleep(8)
    return {"message":"Funcion Async terminada"}
        


def get_fake_user():
    return {
        "username":"Ricardo",
        "role":"admin"
    }
@router.get("/me")
def read_me(user:dict =Depends(get_fake_user)):
    return {**user}
    

@router.get("/test")
def home():
    return {"message": "Hola Mundo, este es mi blog Fastapi"}

#@app.get()
@router.get("",response_model=PaginatedPostAdvance, response_model_exclude_none=True)
#!personalizamos el argumento query
def list_posts(
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description="Parametro Obsoleto",
    ),
    query: Optional[str] = Query(
        default=None,
        description="Texto para buscar por titulo",
        alias="search",  # el query param que usara el usuario es search pero internamente se va a procesar la variable query
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$",
        # pattern=r"/[a-zA-Z]+/g",
    ),
    per_page: int = Query(
        10, ge=1, le=50, description="Numero de resultados (1 a 50)"
    ),  # similar a limit
    page: int = Query(
        1, ge=1, description="Numero de paginba >= 1"
    ),  # Cuando usamos el concepto de page siempre se empieza en 1
    # order by se va a limitar a ser o id o title similar a un enum
    order_by: Literal["id", "title"] = Query("id", description="Campo de Orden"),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Direccion de orden asc/desc"
    ),
    db: Session = Depends(get_db),
):
    repository=PostRepository(db)
    query = query or text
    
    (total,items,)=repository.search(query,order_by,direction,page,per_page) # search()devuelve una tupa
    total_pages = math.ceil(total / per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)
    
        
    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    #! Tengo que retornar de la siguiente manera para poder enviar la metadata total,limit,offset y los items
    return PaginatedPostAdvance(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items,  # type: ignore
    )
    
@router.get("/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,  # Tamano de la lista
        description="Uno o mas etiquetas ex: ?tags=python&tags=fastapi",
    ),
    db: Session = Depends(get_db),
):
    repository=PostRepository(db)
    return repository.by_tags(tags)


@router.get(
    "/{post_id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="Post Encontrado",
)
def get_post(
    post_id: int = Path(
        ...,
        ge=1,
        title="Id del Post",
        description="Identificador debe ser mayor a 0",
        example=1,
    ),
    include_content: bool = Query(default=True, description="Incluir content"),
    db: Session = Depends(get_db),
):
    
    
    repository=PostRepository(db)
    post=repository.get(post_id)
    print(f"Antes de la validacion del {post}")
    if not post:
        print(f"entro por esta validacio  {bool(post)}")
        raise HTTPException(status_code=404, detail={
            "message":"Post not found"
        })
        # return {
        #      "message":"Post not found"
        # }
    #!si se incluye el content
    #! usamos PostPublic que incluye content, la clase PostPublic soporta objetos de Sqlalchemy, model_validate() Sirve para validar y transformar datos (diccionarios, ORM objects, etc.) en una instancia de un modelo de Pydantic. Si tuviera false model_validate esperaria un Dict. Devuelve una instancia de PostPublic o PostSummary, lista para serializarse como respuesta JSON.
    
    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)
    return PostSummary.model_validate(post, from_attributes=True)

# Metodo Post
@router.post(
    "",
    response_model=PostPublic,
    response_description="Post Creado (Ok)",
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
#! Body(None)) hace que body sea opcional osea puede venir o no. Si hay que obligarlo hay que usar elipsis (...)
# def create_post(body: dict=Body(...)):
#! Annotated[PostCreate,Depends(PostCreate.as_form)] con esto le damos los atributos de un formulario
async def create_post(body: Annotated[PostCreate,Depends(PostCreate.as_form)],image:Optional[UploadFile]=File(None), db: Session = Depends(get_db),user=Depends(get_current_user)):
    print(f"body: {body}")
    repository=PostRepository(db)
    saved=None
      
    try:
        if image:
            saved=await save_uploaded_image(image)
            
        image_url=saved["url"] if saved else ""    
        post = repository.create_post(
        title=body.title,
        content= body.content, # type: ignore
        #author= body.author.model_dump() if body.author else None, #Con model_dump() convertimos de objeto a dict
        author=user,# le asigno el user que se obtiene de get_current_user
        tags=[tag.model_dump() for tag in body.tags],image_url=image_url)
        #!Confirmar con commit
        db.commit()
        #! Traer los datos finales como el id y el created_at
        db.refresh(post)
        return post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="EL titulo ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")

@router.put(
    "/{post_id}",
    response_model=PostPublic,
    response_description="Post Modificado",
    response_model_exclude_none=True # Excluimos los valores que sean None con response_model_exclude
)  
#! el body sera obligatorio con elipsis (...)
# def update_post(post_id:int, body:dict=Body(...)):
def update_post(post_id: int, body: PostUpdate, db: Session = Depends(get_db),user=Depends(get_current_user)):
    print(f"body.title {body.title}")
    print(f"body.content {body.content}")
    
    repository=PostRepository(db)   
    post=repository.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    try:
        #!#Con model_dump convertimos de un objeto a un dict/ Con exclude_unset=true evito de que en los values vengan None como por ejemplo en los valores None por defecto definidos en los campos de los modelos de pydantic como en el modelo PostUpdate
        updates = body.model_dump(exclude_unset=True)
        post=repository.update_post(post,updates)
        db.commit()
        db.refresh(post)
        return post
    except SQLAlchemyError as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el post")

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db),user=Depends(get_current_user)):
    print(f"Entro al Router Delete post")
    repository=PostRepository(db)
    
    post = repository.get(post_id)
    print(f"Router Delete post: {post}")
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    try:
        repository.delete_post(post)
        db.commit()
    except SQLAlchemyError as e:
        print(e)
        db.rollback()

@router.get("/secure")
def secure_endpoint(token:str=Depends(oauth2_schema)):
    return {
        "message":"Acceso con token",
        "token_recibido":token
    }

