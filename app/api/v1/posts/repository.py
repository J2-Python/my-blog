from math import ceil
from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload, joinedload
from typing import Optional, Tuple, List
from app.models import PostORM, TagORM,User
from app.core.security import get_current_user


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int) -> Optional[PostORM]:
        #!Usamos get cuando la busqueda es por el pk
        # post=db.get(PostORM,post_id)
        #!Usamos select cuando se quiere usar filtros
        post_find = select(PostORM).where(PostORM.id == post_id)
        result = self.db.execute(
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
            .options(selectinload(PostORM.tags), joinedload(PostORM.user))
            .where(PostORM.tags.any(func.lower(TagORM.name).in_(normalized_tag_names)))
            .order_by(PostORM.id.asc())
        )
        #!Hacemos la conversionde Sequence[PostORM] a -> List[PostORM]
        return list(self.db.execute(post_list).scalars().all())

    def ensure_author(self, name: str, email: str) -> User|None:

        author_obj = self.db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
        print(f"author_obj {author_obj}")
        
        # if not author_obj:
        #     #! Creo el objeto author_obj que es de tipo AuthorORM
        #     author_obj = User(name=name, email=email)
        #     print(f"Author {author_obj}")
        #     self.db.add(author_obj)
        #     self.db.flush()  #! aseguramos que el author ya este disponible sin necesidad de hacer el commit
        return author_obj

    def ensure_tag(self, name: str) -> TagORM:
        normalize=name.strip().lower()
        tag_obj = self.db.execute(
            #para la version sqlite:
            #select(TagORM).where(func.lower(TagORM.name)==normalize)
            select(TagORM).where(TagORM.name.ilike(normalize))
        ).scalar_one_or_none()
        if not tag_obj:
            tag_obj = TagORM(name=normalize)
            self.db.add(tag_obj)
            self.db.flush

        return tag_obj

    def create_post(
        self,
        title: str,
        content: str,
        tags: list[dict],
        image_url: str,
        category_id:Optional[int],
        user: User=Depends(get_current_user),
    ) -> PostORM:
        user_obj = None
        if user:
            # author_obj = self.ensure_author(author["name"], author["email"])
            user_obj = self.ensure_author(user.full_name, user.email)

        post = PostORM(
            title=title, content=content, user=user_obj, image_url=image_url,category_id=category_id
        )
        print(f"tags items {tags}")
        #!Creamos una lista de tags ['python','fastapi']
        names = tags[0]["name"].split(
            ","
        )  # en esta implemenmtacion tags siempre va a venir como una lista de un solo elemento en este caso de un diccionario Ex: [{'name': 'python,fastapi'}]
        print(f"Names tags items {names}")
        for name in names:
            name = name.strip().lower()
            if not name:
                continue
            tag_obj = self.ensure_tag(name)
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
        # self.db.add(post) #No es necesario porque en el router hago el commit()

        return post

    def delete_post(self, post: PostORM) -> None:
        self.db.delete(post)
