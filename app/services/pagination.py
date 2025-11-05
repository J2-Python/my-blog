from math import ceil
from typing import Any, Dict, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
DEFAULT_PER_PAGE=10
MAX_PER_PAGE=100

def sanitize_pagination(page:int=1,per_page:int=DEFAULT_PER_PAGE):
    page=max(1,int(page or 1)) # que la pagina al menos siempre sea 1
    per_page=min(MAX_PER_PAGE,max(1,int(per_page or DEFAULT_PER_PAGE)))
    #! Retornamos una tupla
    return page,per_page

def paginate_query(
    db:Session,
    model,
    base_query=None,
    page:int=1,
    per_page:int=DEFAULT_PER_PAGE,
    order_by:Optional[str]=None,
    direction:str="asc",
    allowed_order:Optional[Dict[str,Any]]=None
    
):
    print(f"pagination.paginate_query: {base_query}")
    page,per_page=sanitize_pagination(page,per_page)
    print(f"base_query.__bool__(): {base_query.__bool__} type {type(base_query)} , {base_query}")
    query=base_query if base_query is not None else select(model) # base_query es igual a SELECT tags.id, tags.name y no se puede evualar como un truly porque en caso de que si venga un objeto de sqlalchemy no tiene definido el atributo Boolean y es necesario evaluarlo como is not None
    total=db.scalar(select(func.count()).select_from(model)) or 0 
    print(f"paginate_query: {total}")
    
    if total ==0:
        return {
            "total":0,
            "pages":0,
            "page":page,
            "per_page":per_page,
            "items":[]
        }
    
    if allowed_order and order_by:
        #col=allowed_order.get(order_by,"id")
        
        col=allowed_order.get(order_by,allowed_order.get("id"))
        print(f"col: {col}")
        if col:
            query=query.order_by(col.desc() if direction=="desc" else col.asc())
    
    items=db.execute(query.offset((page-1) * per_page).limit(per_page)).scalars().all()
    return {
            "total":total,
            "pages":ceil(total/per_page),
            "page":page,
            "per_page":per_page,
            "items":items
        }
    