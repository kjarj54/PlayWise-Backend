from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, delete
from typing import List, Optional

from app.db.database import get_session
from app.core.auth import get_current_user, get_current_user_optional, get_admin_user
from app.models import (
    User,
    CommentUser,
    CommentCreate,
    CommentCreateRequest,
    CommentUpdate,
    CommentRead,
    CommentReadWithUser,
    CommentReadWithReplies
)
from app.services.comment_service import CommentService


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_data: CommentCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment on a game.
    - Can be a top-level comment or a reply to another comment.
    - Supports api_id (RAWG game ID) or game_id (internal DB ID).
    - If api_id is provided and game doesn't exist, it will be created automatically.
    """
    comment = CommentService.create_comment(
        session=session,
        user_id=current_user.id,
        comment_data=comment_data
    )
    return comment


@router.get("/game/{game_id}", response_model=List[CommentReadWithUser])
def get_game_comments(
    game_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get all top-level comments for a specific game.
    - Returns only root comments (not replies).
    - If authenticated, includes user's private comments.
    """
    user_id = current_user.id if current_user else None
    comments = CommentService.get_comments_by_game(
        session=session,
        game_id=game_id,
        skip=skip,
        limit=limit,
        user_id=user_id
    )
    return comments


@router.get("/api/{api_id}", response_model=List[CommentReadWithUser])
def get_game_comments_by_api_id(
    api_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get all top-level comments for a specific game by its RAWG API ID.
    - Returns only root comments (not replies).
    - If authenticated, includes user's private comments.
    - Useful for frontend that uses RAWG IDs.
    """
    user_id = current_user.id if current_user else None
    comments = CommentService.get_comments_by_api_id(
        session=session,
        api_id=api_id,
        skip=skip,
        limit=limit,
        user_id=user_id
    )
    return comments


@router.get("/{comment_id}", response_model=CommentReadWithReplies)
def get_comment_with_replies(
    comment_id: int,
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get a specific comment with all its replies.
    - Useful for viewing comment threads.
    """
    user_id = current_user.id if current_user else None
    comment = CommentService.get_comment_with_replies(
        session=session,
        comment_id=comment_id,
        user_id=user_id
    )
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    return comment


@router.get("/user/{user_id}", response_model=List[CommentReadWithUser])
def get_user_comments(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get all comments by a specific user.
    - If viewing own comments, includes private ones.
    - If viewing others', only public comments are shown.
    """
    requesting_user_id = current_user.id if current_user else None
    comments = CommentService.get_user_comments(
        session=session,
        user_id=user_id,
        skip=skip,
        limit=limit,
        requesting_user_id=requesting_user_id
    )
    return comments


@router.put("/{comment_id}", response_model=CommentRead)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a comment.
    - Only the comment owner can edit it.
    - Marks the comment as edited.
    """
    comment = CommentService.update_comment(
        session=session,
        comment_id=comment_id,
        user_id=current_user.id,
        comment_data=comment_data
    )
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a comment.
    - Only the comment owner can delete it.
    - Also deletes all replies to this comment.
    """
    CommentService.delete_comment(
        session=session,
        comment_id=comment_id,
        user_id=current_user.id
    )
    return None


@router.post("/{comment_id}/like", response_model=CommentRead)
def like_comment(
    comment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Like a comment.
    Creates a like record for this user if not already liked.
    """
    comment, user_has_liked = CommentService.toggle_like(
        session=session,
        comment_id=comment_id,
        user_id=current_user.id,
        increment=True
    )
    return comment


@router.post("/{comment_id}/unlike", response_model=CommentRead)
def unlike_comment(
    comment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Unlike a comment.
    Removes the like record for this user if exists.
    """
    comment, user_has_liked = CommentService.toggle_like(
        session=session,
        comment_id=comment_id,
        user_id=current_user.id,
        increment=False
    )
    return comment


@router.get("/{comment_id}/has-liked")
def check_has_liked(
    comment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Check if the current user has liked this comment.
    Returns: {"has_liked": true/false}
    """
    has_liked = CommentService.has_user_liked(
        session=session,
        comment_id=comment_id,
        user_id=current_user.id
    )
    return {"has_liked": has_liked}


@router.delete("/admin/clear-all", status_code=status.HTTP_200_OK)
def clear_all_comments(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user)
):
    """
    [ADMIN ONLY] Delete all comments from the database.
    This is a dangerous operation and should only be used for cleanup.
    """
    # Count comments before deletion
    count_query = select(CommentUser)
    comments = session.exec(count_query).all()
    count = len(comments)
    
    # Delete all comments
    session.exec(delete(CommentUser))
    session.commit()
    
    return {
        "message": "All comments deleted successfully",
        "deleted_count": count
    }
