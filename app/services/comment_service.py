from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.models import (
    CommentUser,
    CommentCreate,
    CommentCreateRequest,
    CommentUpdate,
    CommentReadWithUser,
    CommentReadWithReplies,
    CommentLike,
    User,
    Game,
    GameCreate
)


class CommentService:
    """Service for handling comment operations"""
    
    @staticmethod
    def get_or_create_game(
        session: Session,
        api_id: Optional[str] = None,
        game_id: Optional[int] = None,
        game_name: Optional[str] = None
    ) -> Game:
        """Get or create a game by api_id or game_id"""
        
        # If game_id provided, use it directly
        if game_id:
            game = session.get(Game, game_id)
            if game:
                return game
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with id {game_id} not found"
            )
        
        # If api_id provided, search or create
        if api_id:
            # Search for existing game
            statement = select(Game).where(Game.api_id == api_id)
            game = session.exec(statement).first()
            
            if game:
                return game
            
            # Create new game
            game_data = GameCreate(
                name=game_name or f"Game {api_id}",
                api_id=api_id
            )
            
            new_game = Game(**game_data.model_dump())
            session.add(new_game)
            session.commit()
            session.refresh(new_game)
            return new_game
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either game_id or api_id must be provided"
        )
    
    @staticmethod
    def create_comment(
        session: Session,
        user_id: int,
        comment_data: CommentCreateRequest
    ) -> CommentUser:
        """Create a new comment"""
        
        # Get or create game
        game = CommentService.get_or_create_game(
            session=session,
            api_id=comment_data.api_id,
            game_id=comment_data.game_id,
            game_name=comment_data.game_name
        )
        
        # If replying to a comment, verify parent exists
        if comment_data.parent_comment_id:
            parent_comment = session.get(CommentUser, comment_data.parent_comment_id)
            if not parent_comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent comment not found"
                )
            
            # Verify parent comment is for the same game
            if parent_comment.game_id != game.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent comment is not for this game"
                )
        
        # Create comment
        db_comment = CommentUser(
            user_id=user_id,
            game_id=game.id,
            content=comment_data.content,
            is_public=comment_data.is_public,
            parent_comment_id=comment_data.parent_comment_id
        )
        
        session.add(db_comment)
        session.commit()
        session.refresh(db_comment)
        
        return db_comment
    
    @staticmethod
    def get_comment_by_id(
        session: Session,
        comment_id: int
    ) -> Optional[CommentUser]:
        """Get a comment by ID"""
        return session.get(CommentUser, comment_id)
    
    @staticmethod
    def get_comments_by_api_id(
        session: Session,
        api_id: str,
        skip: int = 0,
        limit: int = 50,
        include_private: bool = False,
        user_id: Optional[int] = None
    ) -> List[CommentReadWithUser]:
        """Get all comments for a game by its api_id (RAWG ID)"""
        
        # Find game by api_id
        statement = select(Game).where(Game.api_id == api_id)
        game = session.exec(statement).first()
        
        if not game:
            # No game found, return empty list
            return []
        
        # Get comments for this game
        return CommentService.get_comments_by_game(
            session=session,
            game_id=game.id,
            skip=skip,
            limit=limit,
            include_private=include_private,
            user_id=user_id
        )
    
    @staticmethod
    def get_comments_by_game(
        session: Session,
        game_id: int,
        skip: int = 0,
        limit: int = 50,
        include_private: bool = False,
        user_id: Optional[int] = None
    ) -> List[CommentReadWithUser]:
        """Get all comments for a specific game (only top-level comments)"""
        
        query = select(CommentUser, User).join(User).where(
            CommentUser.game_id == game_id,
            CommentUser.parent_comment_id == None  # Only root comments
        )
        
        # Filter visibility
        if not include_private:
            query = query.where(CommentUser.is_public == True)
        elif user_id:
            # Show only user's private comments
            query = query.where(
                (CommentUser.is_public == True) | (CommentUser.user_id == user_id)
            )
        
        query = query.offset(skip).limit(limit).order_by(CommentUser.created_at.desc())
        
        results = session.exec(query).all()
        
        comments_with_user = []
        for comment, user in results:
            comment_dict = {
                "id": comment.id,
                "user_id": comment.user_id,
                "game_id": comment.game_id,
                "content": comment.content,
                "is_public": comment.is_public,
                "is_edited": comment.is_edited,
                "parent_comment_id": comment.parent_comment_id,
                "likes_count": comment.likes_count,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "username": user.username,
                "user_profile_picture": user.profile_picture
            }
            comments_with_user.append(CommentReadWithUser(**comment_dict))
        
        return comments_with_user
    
    @staticmethod
    def get_comment_with_replies(
        session: Session,
        comment_id: int,
        user_id: Optional[int] = None
    ) -> Optional[CommentReadWithReplies]:
        """Get a comment with all its replies"""
        
        # Get parent comment
        result = session.exec(
            select(CommentUser, User)
            .join(User)
            .where(CommentUser.id == comment_id)
        ).first()
        
        if not result:
            return None
        
        comment, user = result
        
        # Get replies
        replies_query = select(CommentUser, User).join(User).where(
            CommentUser.parent_comment_id == comment_id
        )
        
        # Filter visibility for replies
        if user_id:
            replies_query = replies_query.where(
                (CommentUser.is_public == True) | (CommentUser.user_id == user_id)
            )
        else:
            replies_query = replies_query.where(CommentUser.is_public == True)
        
        replies_query = replies_query.order_by(CommentUser.created_at.asc())
        replies_results = session.exec(replies_query).all()
        
        # Build replies list
        replies = []
        for reply, reply_user in replies_results:
            reply_dict = {
                "id": reply.id,
                "user_id": reply.user_id,
                "game_id": reply.game_id,
                "content": reply.content,
                "is_public": reply.is_public,
                "is_edited": reply.is_edited,
                "parent_comment_id": reply.parent_comment_id,
                "likes_count": reply.likes_count,
                "created_at": reply.created_at,
                "updated_at": reply.updated_at,
                "username": reply_user.username,
                "user_profile_picture": reply_user.profile_picture
            }
            replies.append(CommentReadWithUser(**reply_dict))
        
        # Build parent comment with replies
        comment_dict = {
            "id": comment.id,
            "user_id": comment.user_id,
            "game_id": comment.game_id,
            "content": comment.content,
            "is_public": comment.is_public,
            "is_edited": comment.is_edited,
            "parent_comment_id": comment.parent_comment_id,
            "likes_count": comment.likes_count,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "username": user.username,
            "user_profile_picture": user.profile_picture,
            "replies": replies
        }
        
        return CommentReadWithReplies(**comment_dict)
    
    @staticmethod
    def get_user_comments(
        session: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        requesting_user_id: Optional[int] = None
    ) -> List[CommentReadWithUser]:
        """Get all comments by a specific user"""
        
        query = select(CommentUser, User).join(User).where(
            CommentUser.user_id == user_id
        )
        
        # Filter visibility
        if requesting_user_id != user_id:
            # Only show public comments if not the owner
            query = query.where(CommentUser.is_public == True)
        
        query = query.offset(skip).limit(limit).order_by(CommentUser.created_at.desc())
        
        results = session.exec(query).all()
        
        comments_with_user = []
        for comment, user in results:
            comment_dict = {
                "id": comment.id,
                "user_id": comment.user_id,
                "game_id": comment.game_id,
                "content": comment.content,
                "is_public": comment.is_public,
                "is_edited": comment.is_edited,
                "parent_comment_id": comment.parent_comment_id,
                "likes_count": comment.likes_count,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "username": user.username,
                "user_profile_picture": user.profile_picture
            }
            comments_with_user.append(CommentReadWithUser(**comment_dict))
        
        return comments_with_user
    
    @staticmethod
    def update_comment(
        session: Session,
        comment_id: int,
        user_id: int,
        comment_data: CommentUpdate
    ) -> CommentUser:
        """Update a comment"""
        
        db_comment = session.get(CommentUser, comment_id)
        if not db_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Verify ownership
        if db_comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own comments"
            )
        
        # Update fields
        update_data = comment_data.model_dump(exclude_unset=True)
        
        if update_data:
            for key, value in update_data.items():
                setattr(db_comment, key, value)
            
            # Mark as edited if content changed
            if "content" in update_data:
                db_comment.is_edited = True
            
            db_comment.updated_at = datetime.now(timezone.utc)
            
            session.add(db_comment)
            session.commit()
            session.refresh(db_comment)
        
        return db_comment
    
    @staticmethod
    def delete_comment(
        session: Session,
        comment_id: int,
        user_id: int
    ) -> bool:
        """Delete a comment and all its replies"""
        
        db_comment = session.get(CommentUser, comment_id)
        if not db_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Verify ownership
        if db_comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments"
            )
        
        # Delete all replies first
        replies = session.exec(
            select(CommentUser).where(CommentUser.parent_comment_id == comment_id)
        ).all()
        
        for reply in replies:
            session.delete(reply)
        
        # Delete the comment
        session.delete(db_comment)
        session.commit()
        
        return True
    
    @staticmethod
    def toggle_like(
        session: Session,
        comment_id: int,
        user_id: int,
        increment: bool = True
    ) -> tuple[CommentUser, bool]:
        """
        Toggle like/unlike on a comment with user tracking.
        
        Args:
            session: Database session
            comment_id: ID of the comment to like/unlike
            user_id: ID of the user liking/unliking
            increment: True to like, False to unlike
            
        Returns:
            Tuple of (Updated comment, user_has_liked status)
            
        Raises:
            HTTPException: If comment not found
        """
        db_comment = session.get(CommentUser, comment_id)
        if not db_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Check if user already liked this comment
        existing_like = session.exec(
            select(CommentLike).where(
                CommentLike.user_id == user_id,
                CommentLike.comment_id == comment_id
            )
        ).first()
        
        if increment:
            # User wants to like
            if existing_like:
                # Already liked, don't do anything
                return db_comment, True
            else:
                # Create new like
                new_like = CommentLike(
                    user_id=user_id,
                    comment_id=comment_id,
                    created_at=datetime.now(timezone.utc)
                )
                session.add(new_like)
        else:
            # User wants to unlike
            if existing_like:
                # Remove the like
                session.delete(existing_like)
            else:
                # Not liked, don't do anything
                return db_comment, False
        
        session.commit()
        
        # Recalculate likes_count from CommentLike table
        likes_count = session.exec(
            select(CommentLike).where(CommentLike.comment_id == comment_id)
        ).all()
        db_comment.likes_count = len(likes_count)
        
        session.add(db_comment)
        session.commit()
        session.refresh(db_comment)
        
        # Return updated comment and current liked status
        user_has_liked = increment if increment else False
        return db_comment, user_has_liked
    
    @staticmethod
    def has_user_liked(
        session: Session,
        comment_id: int,
        user_id: int
    ) -> bool:
        """
        Check if a user has liked a specific comment.
        
        Args:
            session: Database session
            comment_id: ID of the comment
            user_id: ID of the user
            
        Returns:
            True if user has liked the comment, False otherwise
        """
        existing_like = session.exec(
            select(CommentLike).where(
                CommentLike.user_id == user_id,
                CommentLike.comment_id == comment_id
            )
        ).first()
        
        return existing_like is not None
