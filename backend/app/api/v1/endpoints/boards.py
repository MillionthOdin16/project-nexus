"""
Board endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.sqlmodels import Board, List, User
from app.models.schemas import BoardCreate, BoardUpdate, BoardResponse, BoardWithLists
from app.core.security import get_current_user

router = APIRouter()


async def get_board_with_access(board_id: UUID, user_id: UUID, db: AsyncSession) -> Board:
    """Get board and verify access"""
    result = await db.execute(
        select(Board)
        .options(selectinload(Board.lists).selectinload(List.cards))
        .where(Board.id == board_id)
    )
    board = result.scalar_one_or_none()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check access
    if board.owner_id != user_id and not user_id:  # user_id would be None for unauth
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this board"
        )
    
    return board


@router.get("", response_model=List[BoardResponse])
async def list_boards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all boards the user has access to"""
    # Get boards owned by user
    result = await db.execute(
        select(Board).where(Board.owner_id == current_user.id)
    )
    owned_boards = result.scalars().all()
    
    # Get boards shared with user
    result = await db.execute(
        select(Board)
        .join(Board.members)
        .where(Board.members.any(user_id=current_user.id))
    )
    shared_boards = result.scalars().all()
    
    # Combine and return
    all_boards = list(owned_boards) + [b for b in shared_boards if b not in owned_boards]
    return all_boards


@router.post("", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
async def create_board(
    board_data: BoardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new board"""
    board = Board(
        name=board_data.name,
        description=board_data.description,
        owner_id=current_user.id
    )
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board


@router.get("/{board_id}", response_model=BoardWithLists)
async def get_board(
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific board with all lists and cards"""
    # Get board with lists and cards
    result = await db.execute(
        select(Board)
        .options(
            selectinload(Board.lists).selectinload(List.cards)
        )
        .where(Board.id == board_id)
    )
    board = result.scalar_one_or_none()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check access
    if board.owner_id != current_user.id and not current_user.is_admin:
        # Check if user is a member
        is_member = any(m.user_id == current_user.id for m in board.members)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this board"
            )
    
    # Sort lists by position
    board.lists = sorted(board.lists, key=lambda x: x.position)
    for list_obj in board.lists:
        list_obj.cards = sorted(list_obj.cards, key=lambda x: x.position)
    
    return board


@router.put("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: UUID,
    board_data: BoardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a board"""
    result = await db.execute(
        select(Board).where(Board.id == board_id)
    )
    board = result.scalar_one_or_none()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check ownership
    if board.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this board"
        )
    
    # Update fields
    if board_data.name is not None:
        board.name = board_data.name
    if board_data.description is not None:
        board.description = board_data.description
    if board_data.is_shared is not None:
        board.is_shared = board_data.is_shared
    
    await db.commit()
    await db.refresh(board)
    return board


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a board"""
    result = await db.execute(
        select(Board).where(Board.id == board_id)
    )
    board = result.scalar_one_or_none()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # Check ownership
    if board.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this board"
        )
    
    await db.delete(board)
    await db.commit()
    return None
