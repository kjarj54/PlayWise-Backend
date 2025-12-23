# =========================
# MODELS EXPORTS
# =========================

# User models
from .user import (
    User, 
    UserBase, 
    UserCreate, 
    UserCreateGoogle,
    UserRead, 
    UserReadPrivate,
    UserUpdate,
    UserUpdatePassword,
    UserResetPassword,
    UserRole,
    AuthProvider
)

# Game models
from .game import (
    Game,
    GameBase,
    GameCreate,
    GameRead,
    GameUpdate,
    GameSearch
)

# WishList models
from .wishlist import (
    WishList,
    WishListBase,
    WishListCreate,
    WishListRead,
    WishListReadWithGame
)

# Calification models
from .calification import (
    CalificationGame,
    CalificationGameBase,
    CalificationCreate,
    CalificationRead,
    CalificationReadWithDetails,
    CalificationUpdate,
    GameCalificationStats
)

# Comment models
from .comment import (
    CommentUser,
    CommentUserBase,
    CommentCreate,
    CommentRead,
    CommentReadWithUser,
    CommentReadWithReplies,
    CommentUpdate
)

# Store models
from .store import (
    Store,
    StoreBase,
    StoreCreate,
    StoreRead,
    StoreReadWithGame,
    StoreUpdate
)

# Friend models
from .friend import (
    Friend,
    FriendBase,
    FriendStatus,
    FriendRequestCreate,
    FriendRequestResponse,
    FriendRead,
    FriendReadWithUser,
    FriendListResponse,
    PendingRequestsResponse,
    BlockedUsersResponse
)


__all__ = [
    # User
    "User", "UserBase", "UserCreate", "UserCreateGoogle", "UserRead", 
    "UserReadPrivate", "UserUpdate", "UserUpdatePassword", "UserResetPassword",
    "UserRole", "AuthProvider",
    
    # Game
    "Game", "GameBase", "GameCreate", "GameRead", "GameUpdate", "GameSearch",
    
    # WishList
    "WishList", "WishListBase", "WishListCreate", "WishListRead", "WishListReadWithGame",
    
    # Calification
    "CalificationGame", "CalificationGameBase", "CalificationCreate", 
    "CalificationRead", "CalificationReadWithDetails", "CalificationUpdate",
    "GameCalificationStats",
    
    # Comment
    "CommentUser", "CommentUserBase", "CommentCreate", "CommentRead",
    "CommentReadWithUser", "CommentReadWithReplies", "CommentUpdate",
    
    # Store
    "Store", "StoreBase", "StoreCreate", "StoreRead", "StoreReadWithGame", "StoreUpdate",
    
    # Friend
    "Friend", "FriendBase", "FriendStatus", "FriendRequestCreate",
    "FriendRequestResponse", "FriendRead", "FriendReadWithUser",
    "FriendListResponse", "PendingRequestsResponse", "BlockedUsersResponse",
]
