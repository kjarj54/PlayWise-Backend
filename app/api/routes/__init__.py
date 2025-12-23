"""
API Routes exports
"""

from .auth import router as auth_router
from .user_routes import router as user_router
from .game_routes import router as game_router
from .wishlist_routes import router as wishlist_router
from .calification_routes import router as calification_router
from .friend_routes import router as friend_router


__all__ = [
    "auth_router",
    "user_router",
    "game_router",
    "wishlist_router",
    "calification_router",
    "friend_router",
]
