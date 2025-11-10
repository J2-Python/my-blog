import time
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
BLACKLIST={}

def register_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5555", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        print(f"start_time: {start_time}")
        #!Esperamso a que se resuelva el request
        response = await call_next(request)
        end_time = time.perf_counter()
        print(f"end_time: {end_time}") 
        process_time=end_time -start_time
        #!Agregamos al header http
        response.headers["X-Process-Time"]=f"{process_time:.4f}"
        return response
    
    @app.middleware("http")
    async def log_request(request:Request,call_next):
        print(f"**Entrada: {request.method} {request.url} **")
        response=await call_next(request)
        print(f"**Salida: {response.status_code}  **")
        return response
    
    @app.middleware("http")
    async def add_request_id_header(request:Request,call_next):
        requeste_id=str(uuid.uuid4())
        response=await call_next(request)
        #!Agregamos al header http
        response.headers["X-Request-ID"]=f"{requeste_id}"
        return response
    
    @app.middleware("http")
    async def block_ip_middleware(request:Request,call_next):
        ip_client = request.client.host if request.client else "0.0.0.0"
        if ip_client in BLACKLIST:
            raise HTTPException(status_code=403,detail="Acceso no autorizado")
        return await call_next(request)
        