"""
Services module exports
"""

from .user_service import UserService
from .auth_service import AuthService
from .game_service import GameService
from .wishlist_service import WishListService
from .calification_service import CalificationService
from .friend_service import FriendService
from .otp_service import OTPService


__all__ = [
    "UserService",
    "AuthService",
    "GameService",
    "WishListService",
    "CalificationService",
    "FriendService",
    "OTPService",
]
