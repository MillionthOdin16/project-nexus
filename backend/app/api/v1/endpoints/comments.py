"""
Comments endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sqlmodels import Comment, Card, List, Board, User
from app.models.schemas import CommentCreate, CommentResponse
from app.core.security import get_current_user
from app.api.v1.endpoints.lists import check_board_access

router = APIRouter()


async def get_card_board_id(card_id: UUID, db: AsyncSession) -> UUID:
    """Get board ID for a card"""
    result = await db.execute(select(Card).where(Card.id == card_id))
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    result = await db.execute(select(List).where(List.id == card.list_id))
    list_obj = result.scalar_one_or_none()
    
    return list_obj.board_id


@router.get("/card/{card_id}", response_model=List[CommentResponse])
async def list_comments(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all comments for a card"""
    # Check board access
    board_id = await get_card_board_id(card_id, db)
    has_access = await check_board_access(board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this card"
        )
    
    result = await db.execute(
        select(Comment).where(Comment.card_id == card_id).order_by(Comment.created_at)
    )
    comments = result.scalars().all()
    return comments


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new comment"""
    # Check board access
    board_id = await get_card_board_id(comment_data.card_id, db)
    has_access = await check_board_access(board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to comment on this card"
        )
    
    comment = Comment(
        card_id=comment_data.card_id,
        user_id=current_user.id,
        content=comment_data.content
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user is the author
    if comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    await db.delete(comment)
    await db.commit()
    return None
