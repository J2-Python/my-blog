from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
from typing import Annotated, Literal, Optional, List, Union
from fastapi import Form
from app.utils.forbidden_words import FORBIDDEN_WORDS


class Tag(BaseModel):
    name: str = Field(
        ..., min_length=2, max_length=30, description="Nombre de la Etiqueta"
    )
    #! Aceptamos objetos ORM
    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str = Field(..., min_length=3, max_length=20, description="Nombre del Author")
    email: EmailStr = Field(..., description="Correo del Author")
    #! Aceptamos objetos ORM
    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: Optional[str] = None
    # content:str
    # tags: List[Tag] = []
    tags: Optional[List[Tag]] = Field(
        default_factory=list
    )  # Nos crea una lista por cada Post
    author: Optional[Author] = None
    image_url:Optional[str]=None

    #! Aceptamos objetos ORM
    model_config = ConfigDict(from_attributes=True)


class PostCreate(PostBase):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del Post (minimo 3 caracteres maximo 100)",
        examples=["Mi primer post con pydantic Framework"],
    )  # ... significa que espera datos
    content: Optional[str] = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post minimo 10 caracteres",
        examples=["Este es un contenido valido porque tiene 10 caracteres o mas"],
    )

    tags: List[Tag] = Field(default_factory=list)  # Nos crea una lista [] por cada Post
    #!Ya no es necesario porque se va a obtener desde el get_current_user
    #author: Optional[Author] = None

    # Validator Personalizado
    @field_validator("title")
    @classmethod
    def not_allowd_title(cls, value: str) -> str:

        for bad_word in FORBIDDEN_WORDS:
            if bad_word in value.lower():
                raise ValueError(f"Titulo no puede tener la palabra: {bad_word}")
        # si pasa la validacion se devuelve el value
        return value
    @classmethod
    #! Configuramos los atributos de un formulario
    def as_form(
        cls,
        title:Annotated[str,Form(min_length=3)],
        content:Annotated[str,Form(min_length=3)],
        tags:Annotated[Optional[List[str]],Form()]):
        tag_objs=[Tag(name=t) for t in (tags or [])]
        return cls(title=title,content=content,tags=tag_objs)
        #cls.title=title
        #cls.content=content
        #cls.tags=tag_objs


class PostUpdate(BaseModel):
    # en una actualizacion el title es opcional se puede enviar o no
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None)


class PostPublic(PostBase):
    id: int
    #! para que Pydantic esta recibiendo un objeto de SqlAlchemy y lo pueda convertir a un json
    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str
    #! para que Pydantic esta recibiendo un objeto de SqlAlchemy y lo pueda convertir a un json
    # le decimos al PostSumary que aparte de validar dict tambien valide objetos
    model_config = ConfigDict(from_attributes=True)

class PostNotFound(BaseModel):
    message:str
    
class PaginatedPost(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[PostPublic]


class PaginatedPostAdvance(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[PostPublic]