"""
API Routes exports
"""

from .auth import router as auth_router
from .user_routes import router as user_router
from .game_routes import router as game_router
from .wishlist_routes import router as wishlist_router, router_plural as wishlist_router_plural
from .calification_routes import router as calification_router
from .friend_routes import router as friend_router
from .web_pages import router as web_pages_router


__all__ = [
    "auth_router",
    "user_router",
    "game_router",
    "wishlist_router",
    "wishlist_router_plural",
    "calification_router",
    "friend_router",
    "web_pages_router",
]
