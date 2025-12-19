## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
```

2. Activar entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

### Modo desarrollo:
```bash
fastapi dev app/main.py
```

### Modo producción:
```bash
fastapi run app/main.py
```

## Documentación
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Endpoints

- `GET /` - Endpoint raíz
- `GET /hello/` - Hello World simple
- `GET /hello/{name}` - Saludo personalizado


## 🛠️ Comandos de Instalación

```bash
# 1. Crear directorio del proyecto
mkdir mi-proyecto-fastapi
cd mi-proyecto-fastapi

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Crear archivo requirements.txt y agregar las dependencias
# (ver contenido arriba)

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Crear la estructura de carpetas
# (crear manualmente o usar comandos mkdir)

# 7. Ejecutar la aplicación
fastapi dev app/main.py
```