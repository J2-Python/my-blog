from locale import normalize
from pickletools import OpcodeInfo
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.v1.tags.schemas import TagPublic
from app.models import TagORM, PostORM, post_tags

from app.api.v1.posts.repository import PostRepository
from app.models.tag import TagORM
from app.services.pagination import paginate_query


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_tag(self, name) -> TagORM:
        normalize = name.srtip().lower()
        createTag = PostRepository(self.db)
        return createTag.ensure_tag(normalize)

    def list_tags(
        self,
        search: Optional[str],
        order_by: str = "id",
        direction: str = "asc",
        page: int = 1,
        per_page: int = 10,
    ):
        query = select(TagORM)
        if search:
            query = query.where(func.lower(TagORM.name).ilike(f"%{search.lower()}%"))
        allowed_order = {"id": TagORM.id, "name": func.lower(TagORM.name)}
        print(f"repository.list_tags: {query}")
        result = paginate_query(
            db=self.db,
            model=TagORM,
            base_query=query,
            page=page,
            per_page=per_page,
            order_by=order_by,
            direction=direction,
            allowed_order=allowed_order,
        )
        print(f"Antes del model_validate: {result}")
        #!actualizamos el campo result["items"] con los valores convertidos desde Modelos Sqlalchemy o orm a a su equivalente en modelos de pydantic
        result["items"] = [TagPublic.model_validate(item) for item in result["items"]]
        print(f"despues del model_validate: {result}")
        return result

    def update_tag(self, tag: TagORM, updates: dict) -> TagORM:
        # otra opcion es recibiendo name:str y usando self.db.add()
        # if name is not None:
        #     tag.name=name.strip().lower()
        # self.db.add(tag)
        # self.db.flush()ok
        # self.db.refresh(tag)
        # return tag

        for key, value in updates.items():
            setattr(tag, key, value.strip())
        print(f"repository updated_tag: {tag}")
        return tag

    def delete_tag(self, tag: TagORM) -> None:
        # verificar tag si existe
        self.db.delete(tag)

    def get_tag(self, tag_id: int) -> Optional[TagORM | None]:
        tag_find = select(TagORM).where(TagORM.id == tag_id)
        return self.db.execute(tag_find).scalar_one_or_none()

    def most_popular(self) -> dict | None:
        row = (
            self.db.execute(
                select(
                    TagORM.id.label("id"),
                    TagORM.name.label("name"),
                    func.count(PostORM.id).label("uses"),
                )
                .join(post_tags,post_tags.columns.tag_id==TagORM.id)
                .join(PostORM, PostORM.id == post_tags.columns.post_id)
                .group_by(TagORM.id, TagORM.name)
                .order_by(func.count(PostORM.id).desc(), func.lower(TagORM.name).asc())
                .limit(1)  # solo el primer elemento
            )
            .mappings() # convierte de objetos Row o Tuplas a diccionarios, “Devuélveme cada fila como un diccionario (key → value), usando los alias o nombres de columna.”  ex : [{"id": 1, "name": "Python"},{"id": 2, "name": "FastAPI"}]
            .first()  # devuelve la primera fila o None
        )
        #! si no se usara first y en su lugar all()
        # rows = db.execute(query).mappings().all()
        # row = rows[0] if rows else None
        
        #! Ejemplo de la salida de row
        #print(row)
        # {
        #     "id": 3,
        #     "name": "FastAPI",
        #     "uses": 42
        # }
        
        #resultado del print: repository most_popular <class 'sqlalchemy.engine.row.RowMapping'> longitud 3 valor {'id': 11, 'name': 'fastapi', 'uses': 2}
        print(f"repository most_popular {type(row)} longitud {len(row) if row else None} valor {row}")
        #resultado del print: repository most_popular dict {'id': 11, 'name': 'fastapi', 'uses': 2}
        print(f"repository most_popular dict {dict(row) if row else None }")
        
        return dict(row) if row else None