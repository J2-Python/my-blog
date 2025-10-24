from math import ceil
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload, joinedload
from typing import Optional, Tuple, List
from app.models import PostORM, AuthorORM, TagORM


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int) -> Optional[PostORM]:
        #!Usamos get cuando la busqueda es por el pk
        # post=db.get(PostORM,post_id)
        #!Usamos select cuando se quiere usar filtros
        post_find = select(PostORM).where(PostORM.id == post_id)
        result=self.db.execute(
            post_find
        ).scalar_one_or_none()  # Devuelve on objeto PostORM y no un Result
        return result

    def search(
        self,
        query: Optional[str],
        order_by: str,
        direction: str,
        page: int,
        per_page: int,
    ) -> Tuple[int, List[PostORM]]:

        # Logica para ordenamiento
        results = select(PostORM)

        #! si no viene query agarra text
        # query = query or text
        if query:
            results = results.where(PostORM.title.ilike(f"%{query}%"))

        total = (
            self.db.scalar(select(func.count()).select_from(results.subquery())) or 0
        )
        #!Desde aqui ya podemos devolver el resultado en caso de que no haya items
        if total == 0:
            return (0, [])

        #! si alguien envia un valor page que es mayor al total_pages nos aseguramos que en ese escenario siempre devolvamos total_pages y asi aseguramos la aplicacion. es una medida de seguridad.
        current_page = min(page, max(1, ceil(total / per_page)))

        order_col = PostORM.id if order_by == "id" else func.lower(PostORM.title)
        results = results.order_by(
            order_col.asc() if direction == "asc" else order_col.desc()
        )

        print(f"current_page {current_page}")
        print(f"per_page {per_page}")
        start = (current_page - 1) * per_page
        print(f"start: {start}")
        print(f"end: {start + per_page}")
        # items = results[page : page + per_page]
        #!Hacemos la conversionde Sequence[PostORM] a -> List[PostORM]
        items: List[PostORM] = list(
            self.db.execute(results.limit(per_page).offset(start)).scalars().all()
        )

        return (total, items)

    def by_tags(self, tags_names: List[str]) -> List[PostORM]:
        normalized_tag_names = [
            tag.strip().lower() for tag in tags_names if tag.strip()
        ]
        #!En caso de ser una lista vacia
        if not normalized_tag_names:
            return []

        post_list = (
            select(PostORM)
            # joinedload() hace un JOIN y trae los datos relacionados en una sola consulta.
            # selectinload()  hace 2 consultas, pero optimizadas con un IN (...)
            .options(selectinload(PostORM.tags), joinedload(PostORM.author))
            .where(PostORM.tags.any(func.lower(TagORM.name).in_(normalized_tag_names)))
            .order_by(PostORM.id.asc())
        )
        #!Hacemos la conversionde Sequence[PostORM] a -> List[PostORM]
        return list(self.db.execute(post_list).scalars().all())

    def ensure_author(self, name: str, email: str) -> AuthorORM:

        author_obj = self.db.execute(
            select(AuthorORM).where(AuthorORM.email == email)
        ).scalar_one_or_none()
        print(f"author_obj {author_obj}")
        if not author_obj:
            #! Creo el objeto author_obj que es de tipo AuthorORM
            author_obj = AuthorORM(name=name, email=email)
            print(f"Author {author_obj}")
            self.db.add(author_obj)
            self.db.flush()  #! aseguramos que el author ya este disponible sin necesidad de hacer el commit
        return author_obj

    def ensure_tag(self, name: str) -> TagORM:
        tag_obj = self.db.execute(
            select(TagORM).where(TagORM.name.ilike(name))
        ).scalar_one_or_none()
        if not tag_obj:
            tag_obj = TagORM(name=name)
            self.db.add(tag_obj)
            self.db.flush

        return tag_obj

    def create_post(
        self, title: str, content: str, author: Optional[dict], tags: list[dict],image_url:str
    ) -> PostORM:
        author_obj = None
        if author:
            #author_obj = self.ensure_author(author["name"], author["email"])
            author_obj = self.ensure_author(author["username"], author["email"])

        post = PostORM(title=title, content=content, author=author_obj,image_url=image_url)

        for tag in tags:
            tag_obj = self.ensure_tag(tag["name"])
            post.tags.append(tag_obj)

        #!Marcar la insercion
        self.db.add(post)
        #!Confirmar con commit
        self.db.commit()
        #! Traer los datos finales como el id y el created_at
        self.db.refresh(post)
        return post

    def update_post(self, post: PostORM, updates: dict) -> PostORM:

        #!#Con model_dump convertimos de un objeto a un dict/ Con exclude_unset=true evito de que en los values vengan None como por ejemplo en los valores None por defecto definidos en los campos de los modelos de pydantic
        # updates = body.model_dump(exclude_unset=True)
        # Actualizar atributos dinámicamente
        for key, value in updates.items():
            print(f"{key}:{value}")
            setattr(post, key, value)
        #self.db.add(post) #No es necesario porque en el router hago el commit()
        
        return post

    def delete_post(self, post: PostORM) -> None:
        self.db.delete(post)
