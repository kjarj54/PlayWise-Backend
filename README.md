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

## 🎮 PlayWise API - Endpoints

### 🏠 General
- `GET /` - Endpoint raíz de bienvenida
- `GET /hello/` - Hello World simple
- `GET /hello/{name}` - Saludo personalizado

### 🔐 Autenticación
- `POST /api/auth/register` - Registro de nuevos usuarios
- `POST /api/auth/login` - Inicio de sesión
- `POST /api/auth/logout` - Cierre de sesión
- `POST /api/auth/refresh` - Refrescar token de acceso
- `GET /api/auth/me` - Obtener información del usuario autenticado

### 👥 Usuarios
- `GET /api/users` - Listar todos los usuarios
- `GET /api/users/{user_id}` - Obtener usuario por ID
- `PUT /api/users/{user_id}` - Actualizar información del usuario
- `DELETE /api/users/{user_id}` - Eliminar usuario
- `GET /api/users/search` - Buscar usuarios

### 🎯 Juegos
- `GET /api/games` - Listar todos los juegos
- `GET /api/games/{game_id}` - Obtener detalles de un juego
- `POST /api/games` - Crear nuevo juego
- `PUT /api/games/{game_id}` - Actualizar información del juego
- `DELETE /api/games/{game_id}` - Eliminar juego
- `GET /api/games/search` - Buscar juegos por título, género o plataforma

### 🤝 Amigos
- `GET /api/friends` - Listar amigos del usuario
- `POST /api/friends/request` - Enviar solicitud de amistad
- `PUT /api/friends/accept/{request_id}` - Aceptar solicitud de amistad
- `DELETE /api/friends/{friend_id}` - Eliminar amigo
- `GET /api/friends/requests` - Ver solicitudes de amistad pendientes

### 💝 Lista de Deseos
- `GET /api/wishlist` - Ver lista de deseos del usuario
- `POST /api/wishlist` - Agregar juego a la lista de deseos
- `DELETE /api/wishlist/{game_id}` - Eliminar juego de la lista de deseos
- `GET /api/wishlist/shared/{user_id}` - Ver lista de deseos de otro usuario

### ⭐ Calificaciones
- `GET /api/califications/game/{game_id}` - Ver calificaciones de un juego
- `POST /api/califications` - Crear nueva calificación
- `PUT /api/califications/{calification_id}` - Actualizar calificación
- `DELETE /api/califications/{calification_id}` - Eliminar calificación
- `GET /api/califications/user/{user_id}` - Ver calificaciones de un usuario

---

## 🚀 Comandos Útiles

### 📦 Gestión de Dependencias
```bash
# Instalar una nueva dependencia
pip install nombre-paquete

# Actualizar requirements.txt después de instalar paquetes
pip freeze > requirements.txt

# Instalar todas las dependencias
pip install -r requirements.txt

# Actualizar un paquete específico
pip install --upgrade nombre-paquete

# Listar paquetes instalados
pip list

# Desinstalar un paquete
pip uninstall nombre-paquete
```

### 🔧 Desarrollo
```bash
# Ejecutar en modo desarrollo (con auto-reload)
fastapi dev app/main.py

# Ejecutar en modo producción
fastapi run app/main.py

# Ejecutar con Uvicorn directamente (más opciones)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar tests (si tienes pytest configurado)
pytest

# Ver cobertura de tests
pytest --cov=app
```

### 🗄️ Base de Datos
```bash
# Crear migración con Alembic (si lo usas)
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

### 🐛 Debugging y Logs
```bash
# Ver logs en tiempo real
fastapi dev app/main.py --log-level debug

# Ejecutar con más verbosidad
uvicorn app.main:app --reload --log-level debug
```

### 🧪 Testing de Endpoints
```bash
# Usar curl para probar endpoints
curl http://127.0.0.1:8000/

# POST con JSON
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"pass123"}'

# GET con autenticación
curl http://127.0.0.1:8000/api/users/me \
  -H "Authorization: Bearer tu_token_aqui"
```

### 🔄 Git Workflow
```bash
# Ver estado del repositorio
git status

# Agregar cambios
git add .

# Commit con mensaje descriptivo
git commit -m "[FEAT] Descripción del cambio"

# Push a repositorio remoto
git push origin main

# Ver historial de commits
git log --oneline

# Crear una nueva rama
git checkout -b feature/nueva-funcionalidad
```

### 📝 Formato de Código
```bash
# Formatear código con Black (si lo usas)
black app/

# Verificar estilo con flake8
flake8 app/

# Ordenar imports con isort
isort app/
```

---

## 👨‍💻 Creadores

Este proyecto ha sido desarrollado con 💙 por:

- **[Kevin Fallas](https://github.com/kevtico20)** - Full Stack Developer
- **[Kevin Arauz](https://github.com/kjarj54)** - Backend Developer

### 🌟 Características Implementadas
- ✅ Sistema completo de autenticación con JWT
- ✅ Gestión de usuarios y perfiles
- ✅ CRUD de juegos con búsqueda avanzada
- ✅ Sistema de amistades y solicitudes
- ✅ Lista de deseos personalizada
- ✅ Sistema de calificaciones y reseñas
- ✅ Validación de datos con Pydantic
- ✅ Documentación interactiva con Swagger
- ✅ Arquitectura modular y escalable
- ✅ Seguridad con OAuth2 y bcrypt

---

## 📚 Recursos Adicionales

- 📖 [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- 🐍 [Python Documentation](https://docs.python.org/3/)
- 🔐 [OAuth2 con FastAPI](https://fastapi.tiangolo.com/tutorial/security/)
- 💾 [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

---

## 📄 Licencia

Este proyecto es parte de un desarrollo académico/personal.

---

## 🤝 Contribuciones

¿Quieres contribuir? ¡Genial! 
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m '[FEAT] Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

**¡Hecho con ❤️ y mucho ☕ por el equipo de PlayWise!**