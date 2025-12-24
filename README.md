## Installation

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Execution

### Development mode:
```bash
fastapi dev app/main.py
```

### Production mode:
```bash
fastapi run app/main.py
```

## Documentation
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 🎮 PlayWise API - Endpoints

### 🏠 General
- `GET /` - Welcome root endpoint
- `GET /hello/` - Simple Hello World
- `GET /hello/{name}` - Personalized greeting

### 🔐 Authentication
- `POST /api/auth/register` - Register new users
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get authenticated user information

### 👥 Users
- `GET /api/users` - List all users
- `GET /api/users/{user_id}` - Get user by ID
- `PUT /api/users/{user_id}` - Update user information
- `DELETE /api/users/{user_id}` - Delete user
- `GET /api/users/search` - Search users

### 🎯 Games
- `GET /api/games` - List all games
- `GET /api/games/{game_id}` - Get game details
- `POST /api/games` - Create new game
- `PUT /api/games/{game_id}` - Update game information
- `DELETE /api/games/{game_id}` - Delete game
- `GET /api/games/search` - Search games by title, genre, or platform

### 🤝 Friends
- `GET /api/friends` - List user's friends
- `POST /api/friends/request` - Send friend request
- `PUT /api/friends/accept/{request_id}` - Accept friend request
- `DELETE /api/friends/{friend_id}` - Remove friend
- `GET /api/friends/requests` - View pending friend requests

### 💝 Wishlist
- `GET /api/wishlist` - View user's wishlist
- `POST /api/wishlist` - Add game to wishlist
- `DELETE /api/wishlist/{game_id}` - Remove game from wishlist
- `GET /api/wishlist/shared/{user_id}` - View another user's wishlist

### ⭐ Ratings
- `GET /api/califications/game/{game_id}` - View game ratings
- `POST /api/califications` - Create new rating
- `PUT /api/califications/{calification_id}` - Update rating
- `DELETE /api/califications/{calification_id}` - Delete rating
- `GET /api/califications/user/{user_id}` - View user's ratings

---

## 🚀 Useful Commands

### 📦 Dependency Management
```bash
# Install a new dependency
pip install package-name

# Update requirements.txt after installing packages
pip freeze > requirements.txt

# Install all dependencies
pip install -r requirements.txt

# Update a specific package
pip install --upgrade package-name

# List installed packages
pip list

# Uninstall a package
pip uninstall package-name
```

### 🔧 Development
```bash
# Run in development mode (with auto-reload)
fastapi dev app/main.py

# Run in production mode
fastapi run app/main.py

# Run with Uvicorn directly (more options)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests (if you have pytest configured)
pytest

# View test coverage
pytest --cov=app
```

### 🗄️ Database
```bash
# Create migration with Alembic (if you use it)
alembic revision --autogenerate -m "change description"

# Apply migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```

### 🐛 Debugging and Logs
```bash
# View logs in real-time
fastapi dev app/main.py --log-level debug

# Run with more verbosity
uvicorn app.main:app --reload --log-level debug
```

### 🧪 Endpoint Testing
```bash
# Use curl to test endpoints
curl http://127.0.0.1:8000/

# POST with JSON
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"pass123"}'

# GET with authentication
curl http://127.0.0.1:8000/api/users/me \
  -H "Authorization: Bearer your_token_here"
```

### 🔄 Git Workflow
```bash
# View repository status
git status

# Add changes
git add .

# Commit with descriptive message
git commit -m "[FEAT] Change description"

# Push to remote repository
git push origin main

# View commit history
git log --oneline

# Create a new branch
git checkout -b feature/new-functionality
```

### 📝 Code Formatting
```bash
# Format code with Black (if you use it)
black app/

# Check style with flake8
flake8 app/

# Sort imports with isort
isort app/
```

---

## 👨‍💻 Developers

This project has been developed with 💙 by:

- **[Kevin Fallas](https://github.com/kevtico20)** - Full Stack Developer
- **[Kevin Arauz](https://github.com/kjarj54)** - Full Stack Developer

### 🌟 Implemented Features
- ✅ Complete JWT authentication system
- ✅ User and profile management
- ✅ Game CRUD with advanced search
- ✅ Friendship and request system
- ✅ Personalized wishlist
- ✅ Rating and review system
- ✅ Data validation with Pydantic
- ✅ Interactive documentation with Swagger
- ✅ Modular and scalable architecture
- ✅ Security with OAuth2 and bcrypt

---

## 📚 Additional Resources

- 📖 [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 🐍 [Python Documentation](https://docs.python.org/3/)
- 🔐 [OAuth2 with FastAPI](https://fastapi.tiangolo.com/tutorial/security/)
- 💾 [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

---

## 📄 License

This project is part of an academic/personal development.

---

## 🤝 Contributing

Want to contribute? Great! 
1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m '[FEAT] Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Made with ❤️ and lots of ☕ by the PlayWise team!**