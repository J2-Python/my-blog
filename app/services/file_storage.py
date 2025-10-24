from fastapi import UploadFile,HTTPException,status
import os
import shutil
import uuid

MEDIA_DIR="app/media"
ALLOW_MIME=["image/png","image/jpeg"]
MAX_MB=int(os.getenv("MAX_UPLOAD_MB","10"))# usa 10 por defecto
CHUNKS=1024*1024
    
def ensure_media_dir()->None:
    os.makedirs(MEDIA_DIR,exist_ok=True)

async def save_uploaded_image(file:UploadFile)->dict:
    if file.content_type not in ALLOW_MIME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Solo se permiten imagenes PNG o JPEG")
    ensure_media_dir()
    ext=os.path.splitext(file.filename or "")[1] # para obtener la extencion ["nombre","ext"] .png
    print(f"ext: {ext}")
    filename=f"{uuid.uuid4().hex}{ext}" # uuid generara un nombre unico a2918af48df1423587d33425d5569c9d.png
    print(f"filename: {filename}")
    print(f"MEDIA_DIR: {MEDIA_DIR}")  # app/media
    file_path=os.path.join(MEDIA_DIR,filename) # app/media/a2918af48df1423587d33425d5569c9d.png
    print(f"file_path: {file_path}")
    
    # class _ChunkCounter:
    #     def __init__(self, f):
    #         self._f = f
    #         self.calls = 0
    #         self.sizes = []

    #     def read(self, n=-1):
    #         data = self._f.read(n)
    #         if data:
    #             self.calls += 1
    #             self.sizes.append(len(data))
    #         return data

    #     def __getattr__(self, name):  # delega cualquier otro atributo
    #         return getattr(self._f, name)

    # reader = _ChunkCounter(file.file)
    
    with open(file_path,"wb") as buffer: # aqui se conbfigura el nuevo archivo
        #! si usamos _ChunkCounter() en lugar de usar file.file usamos reader
        shutil.copyfileobj(file.file,buffer,length=CHUNKS) # copiamos en el nuevo archivo que esta en el buffer y el archivo se va a dividr en chunks de 1mb
    
    #! Limitamos el tamaño    
    size=os.path.getsize(file_path)
    #traducimos a bytes
    if size >  MAX_MB * CHUNKS:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=f"Archivo demasioado grande (>{MAX_MB} MB)"
        )
    return {
        "filename":filename,
        "content_type":file.content_type,
        "url": f"/media/{filename}",
        "size": size,
        # "chunk_size_used": CHUNKS,
        # "chunk_calls": reader.calls,
        # "chunk_sizes_sample": reader.sizes[:5]
    }