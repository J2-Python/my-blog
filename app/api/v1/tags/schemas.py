from pydantic import BaseModel, ConfigDict, Field


class TagPublic(BaseModel):
    id:int
    name: str = Field(
        ..., min_length=2, max_length=30, description="Nombre de la Etiqueta"
    )
    #! Aceptamos objetos ORM
    model_config = ConfigDict(from_attributes=True)

class TagCreate(BaseModel):
    name: str = Field(
        ..., min_length=2, max_length=30, description="Nombre de la Etiqueta"
    )

class TagUpdate(BaseModel):
    name: str = Field(
        ..., min_length=2, max_length=30, description="Nombre de la Etiqueta"
    )

#Schema para mostrar cuantas veces se esta usando el tag
class TagWithCount(TagPublic):
    uses:int