"""
List endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sqlmodels import List, Board, User
from app.models.schemas import ListCreate, ListUpdate, ListResponse, ListWithCards, ReorderItems
from app.core.security import get_current_user

router = APIRouter()


async def get_list_by_id(list_id: UUID, db: AsyncSession) -> List:
    """Get list by ID"""
    result = await db.execute(select(List).where(List.id == list_id))
    list_obj = result.scalar_one_or_none()
    
    if not list_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    return list_obj


async def check_board_access(board_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    """Check if user has access to the board"""
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    
    if not board:
        return False
    
    if board.owner_id == user_id:
        return True
    
    # Check member
    from app.models.sqlmodels import BoardMember
    result = await db.execute(
        select(BoardMember).where(
            BoardMember.board_id == board_id,
            BoardMember.user_id == user_id
        )
    )
    return result.scalar_one_or_none() is not None


@router.get("/{list_id}", response_model=ListWithCards)
async def get_list(
    list_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific list with all cards"""
    list_obj = await get_list_by_id(list_id, db)
    
    # Check board access
    has_access = await check_board_access(list_obj.board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this list"
        )
    
    # Sort cards by position
    list_obj.cards = sorted(list_obj.cards, key=lambda x: x.position)
    return list_obj


@router.put("/{list_id}", response_model=ListResponse)
async def update_list(
    list_id: UUID,
    list_data: ListUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a list"""
    list_obj = await get_list_by_id(list_id, db)
    
    # Check board access
    has_access = await check_board_access(list_obj.board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this list"
        )
    
    # Update fields
    if list_data.name is not None:
        list_obj.name = list_data.name
    if list_data.color is not None:
        list_obj.color = list_data.color
    if list_data.position is not None:
        list_obj.position = list_data.position
    
    await db.commit()
    await db.refresh(list_obj)
    return list_obj


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    list_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a list"""
    list_obj = await get_list_by_id(list_id, db)
    
    # Check board access
    has_access = await check_board_access(list_obj.board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this list"
        )
    
    await db.delete(list_obj)
    await db.commit()
    return None


@router.post("/reorder", response_model=List[ListResponse])
async def reorder_lists(
    reorder_data: ReorderItems,
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reorder lists within a board"""
    # Check board access
    has_access = await check_board_access(board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this board"
        )
    
    # Update positions
    for item in reorder_data.items:
        result = await db.execute(select(List).where(List.id == item["id"]))
        list_obj = result.scalar_one_or_none()
        if list_obj:
            list_obj.position = item["position"]
    
    await db.commit()
    
    # Return all lists for the board
    result = await db.execute(
        select(List).where(List.board_id == board_id).order_by(List.position)
    )
    lists = result.scalars().all()
    return lists
