"""
Card endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sqlmodels import Card, List, Board, User
from app.models.schemas import CardCreate, CardUpdate, CardResponse, CardMove, ReorderItems
from app.core.security import get_current_user

router = APIRouter()


async def get_card_by_id(card_id: UUID, db: AsyncSession) -> Card:
    """Get card by ID"""
    result = await db.execute(select(Card).where(Card.id == card_id))
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    return card


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


@router.post("/reorder", response_model=List[CardResponse])
async def reorder_cards(
    reorder_data: ReorderItems,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reorder cards within a list"""
    # Update positions
    for item in reorder_data.items:
        result = await db.execute(select(Card).where(Card.id == item["id"]))
        card = result.scalar_one_or_none()
        if card:
            card.position = item["position"]
    
    await db.commit()
    
    # Return all cards in the list (from first item)
    first_item_id = reorder_data.items[0]["id"]
    result = await db.execute(select(Card).where(Card.id == first_item_id))
    card = result.scalar_one_or_none()
    
    if card:
        result = await db.execute(
            select(Card).where(Card.list_id == card.list_id).order_by(Card.position)
        )
        cards = result.scalars().all()
        return cards
    
    return []


@router.post("/move/{card_id}", response_model=CardResponse)
async def move_card(
    card_id: UUID,
    move_data: CardMove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Move a card to a different list"""
    card = await get_card_by_id(card_id, db)
    
    # Get source and target lists
    result = await db.execute(select(List).where(List.id == card.list_id))
    source_list = result.scalar_one_or_none()
    
    result = await db.execute(select(List).where(List.id == move_data.list_id))
    target_list = result.scalar_one_or_none()
    
    if not target_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target list not found"
        )
    
    # Check access to both boards
    has_access = await check_board_access(source_list.board_id, current_user.id, db)
    if not has_access:
        has_access = await check_board_access(target_list.board_id, current_user.id, db)
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to move this card"
        )
    
    # Update card
    card.list_id = move_data.list_id
    card.position = move_data.position
    
    await db.commit()
    await db.refresh(card)
    return card


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific card"""
    card = await get_card_by_id(card_id, db)
    
    # Check board access
    result = await db.execute(select(List).where(List.id == card.list_id))
    list_obj = result.scalar_one_or_none()
    
    has_access = await check_board_access(list_obj.board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this card"
        )
    
    return card


@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: UUID,
    card_data: CardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a card"""
    card = await get_card_by_id(card_id, db)
    
    # Check board access
    result = await db.execute(select(List).where(List.id == card.list_id))
    list_obj = result.scalar_one_or_none()
    
    has_access = await check_board_access(list_obj.board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this card"
        )
    
    # Update fields
    if card_data.title is not None:
        card.title = card_data.title
    if card_data.description is not None:
        card.description = card_data.description
    if card_data.priority is not None:
        card.priority = card_data.priority
    if card_data.due_date is not None:
        card.due_date = card_data.due_date
    if card_data.labels is not None:
        card.labels = card_data.labels
    if card_data.assigned_to is not None:
        card.assigned_to = card_data.assigned_to
    if card_data.is_archived is not None:
        card.is_archived = card_data.is_archived
    
    await db.commit()
    await db.refresh(card)
    return card


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a card"""
    card = await get_card_by_id(card_id, db)
    
    # Check board access
    result = await db.execute(select(List).where(List.id == card.list_id))
    list_obj = result.scalar_one_or_none()
    
    has_access = await check_board_access(list_obj.board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this card"
        )
    
    await db.delete(card)
    await db.commit()
    return None
