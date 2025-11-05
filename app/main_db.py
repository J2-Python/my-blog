from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.db import Base,engine
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.uploads.router import router as upload_router
from app.api.v1.tags.router import router as tag_router
from fastapi.staticfiles import StaticFiles
import os
load_dotenv()
MEDIA_DIR="app/media"
def create_app()->FastAPI:   
    app = FastAPI(title="Mini Blog")
    #!Para crear las tables en la db en caso de que no existan.
    #!Solo aplica para entornos dev, para produccion se usaran migrations
    Base.metadata.create_all(bind=engine) # dev
    app.include_router(auth_router,prefix="/api/v1") #cumple con la ruta /api/v1/auth/login
    app.include_router(post_router)
    app.include_router(upload_router)
    app.include_router(tag_router)
    os.makedirs(MEDIA_DIR,exist_ok=True) #Asegura si la carpeta existe, si no existe makedirs la crea
    #Montamos el directorio /media para poder servir los archivos estaticos.
    app.mount("/media",StaticFiles(directory=MEDIA_DIR),name="media")
    
    return app
app=create_app()