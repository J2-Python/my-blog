from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    slug: str = Field(min_length=2, max_length=60)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    # 👉 los datos son opcionales
    name: str | None = Field(default=None, min_length=2, max_length=60)
    slug: str | None = Field(default=None, min_length=2, max_length=60)


class CategoryPublic(CategoryBase):
    id: int
    # 👉 “Si el objeto no es un dict, intenta obtener los valores de los campos leyendo los atributos del objeto que pueden ser de SQLAlchemy.”.
    # Permite crear el modelo a partir de instancias de clases/ORM, no solo de diccionarios. Internamente hace esto:
    # getattr(category, "id")
    # getattr(category, "name")
    # getattr(category, "slug")
    

    model_config = {"from_attributes": True}
