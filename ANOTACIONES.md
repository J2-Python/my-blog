### Entorno virtual
```
python3 -m venv
```
###  ejecutar entorno virtual
```
source .venv/bin/activate
```
### Instalar fastapi
```
pip install "fastapi[standard]"
```
### Ejecutar Endpoint
```
fastapi dev main.py
```
### Ejecutar Endpoint con uvicorn
```
uvicorn main:app --reload
```

### Verificar puerto 8000 y eliminar puerto 
```
lsof -i :8000
kill -9 <PID>
```
### Instalar SQLAlchemy
```
pip install "sqlalchemy>=2.0"
```

### Instalar driver para Postgres
```
pip install "psycopg[binary]"
```


### Para entrar a la bd
```
psql -U jota -d postgres
o
psql postgres
```

### Lista base de dato
```
\l
```
### Crear DB blog y usario en postgres
```
create database deviblog;
create user blogadmin with password '123456';
grant all privileges on database blog to blogadmin;
```

### Para conectarme a una base de datos en especifico
```
postgres=# \c deviblog
```

### Correr la aplicacion modularizada desde /app
```
fastapi dev app/main_db.py
```

### Instalar PyJWT
```
pip install PyJWT
```

### Configuracion de alembic
```
pip install alembic
```
### En la raiz del proyecto first-steps/
```
alembic init alembic
```
### editar el archivo first-steps/alembic.ini
```
sqlalchemy.url = postgresql+psycopg://blogadmin:123456@localhost:5432/blogfastapi
```
### editar first-steps/alembic/env.py
```
from app.db import Base
from app.models import *  # importa tus modelos
target_metadata = Base.metadata
```
### Generar Migracion y aplicar migracion (ejecutar en la raiz del proyecto no en app/)
```
alembic revision --autogenerate -m "add new field to User model"
alembic upgrade head
```

### Instalar pwdlib passlib
```
pip install pwdlib passlib
```
### Instalar pwdlib[argon2]
```
pip install 'pwdlib[argon2]'
```


### Borrar BD y Generar una migracion Nueva:
```
# 1. Borrar BD
psql -U tu_usuario
DROP DATABASE nombre_de_tu_bd;
CREATE DATABASE nombre_de_tu_bd;

# 2. Borrar versiones viejas
rm -rf alembic/versions/*

# 3. Crear nueva migración
alembic revision --autogenerate -m "initial schema"

# 4. Aplicar
alembic upgrade head
```

### Ejecutar seed
```
python3 -m app.seeds all
```

### slugify
```
pip install python-slugify
```