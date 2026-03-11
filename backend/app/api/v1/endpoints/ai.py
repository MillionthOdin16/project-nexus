"""
AI API endpoints - for Hermes Agent integration
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.session import get_db
from app.models.sqlmodels import Board, Card, List, User
from app.models.schemas import (
    AITaskResponse, AITaskUpdate, BoardResponse, BoardWithLists
)
from app.core.security import get_current_user, get_optional_user

router = APIRouter()


async def verify_ai_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify AI API key"""
    if settings.AI_API_KEY is None:
        # If no AI key configured, allow access (dev mode)
        return True
    
    if x_api_key != settings.AI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True


@router.get("/boards", response_model=List[BoardResponse])
async def ai_list_boards(
    db: AsyncSession = Depends(get_db),
    api_key: bool = Depends(verify_ai_key)
):
    """List all boards accessible to AI (public/shared boards)"""
    # Get all shared boards
    result = await db.execute(
        select(Board).where(Board.is_shared == True)
    )
    boards = result.scalars().all()
    
    # Also get boards owned by the first admin/user (if authenticated)
    return boards


@router.get("/boards/{board_id}", response_model=BoardWithLists)
async def ai_get_board(
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: bool = Depends(verify_ai_key)
):
    """Get a specific board with all lists and cards"""
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
    
    # Sort lists and cards by position
    board.lists = sorted(board.lists, key=lambda x: x.position)
    for list_obj in board.lists:
        list_obj.cards = sorted(list_obj.cards, key=lambda x: x.position)
    
    return board


@router.get("/tasks", response_model=List[AITaskResponse])
async def ai_get_tasks(
    priority: Optional[str] = None,
    board_id: Optional[UUID] = None,
    assigned_only: bool = False,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    api_key: bool = Depends(verify_ai_key)
):
    """Get available tasks for AI to work on.
    
    Returns tasks ordered by priority (urgent > high > medium > low)
    and then by position.
    """
    query = select(Card).options(
        selectinload(Card.list).selectinload(List.board)
    ).where(Card.is_archived == False)
    
    # Filter by board if specified
    if board_id:
        query = query.join(List).where(List.board_id == board_id)
    
    # Filter unassigned tasks (for AI to claim)
    if assigned_only:
        query = query.where(Card.assigned_to != None)
    
    # Order by priority and position
    priority_order = {
        "urgent": 0,
        "high": 1,
        "medium": 2,
        "low": 3
    }
    
    result = await db.execute(query)
    cards = result.scalars().all()
    
    # Sort by priority
    cards.sort(key=lambda c: (priority_order.get(c.priority, 4), c.position))
    
    # Filter by priority if specified
    if priority:
        cards = [c for c in cards if c.priority == priority]
    
    # Limit results
    cards = cards[:limit]
    
    # Transform to response
    tasks = []
    for card in cards:
        task = AITaskResponse(
            id=card.id,
            list_id=card.list_id,
            title=card.title,
            description=card.description,
            position=card.position,
            priority=card.priority,
            due_date=card.due_date,
            labels=card.labels,
            assigned_to=card.assigned_to,
            created_by=card.created_by,
            is_archived=card.is_archived,
            created_at=card.created_at,
            updated_at=card.updated_at,
            board_name=card.list.board.name if card.list else "Unknown",
            list_name=card.list.name if card.list else "Unknown"
        )
        tasks.append(task)
    
    return tasks


@router.post("/tasks/{task_id}/claim", response_model=AITaskResponse)
async def ai_claim_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: bool = Depends(verify_ai_key)
):
    """Claim a task for AI to work on"""
    result = await db.execute(
        select(Card).options(
            selectinload(Card.list).selectinload(List.board)
        ).where(Card.id == task_id)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # For now, set assigned_to to a special AI user ID
    # In production, this would be the AI agent's user ID
    card.assigned_to = None  # Will be set to AI user in production
    
    await db.commit()
    await db.refresh(card)
    
    return AITaskResponse(
        id=card.id,
        list_id=card.list_id,
        title=card.title,
        description=card.description,
        position=card.position,
        priority=card.priority,
        due_date=card.due_date,
        labels=card.labels,
        assigned_to=card.assigned_to,
        created_by=card.created_by,
        is_archived=card.is_archived,
        created_at=card.created_at,
        updated_at=card.updated_at,
        board_name=card.list.board.name if card.list else "Unknown",
        list_name=card.list.name if card.list else "Unknown"
    )


@router.post("/tasks/{task_id}/complete", response_model=AITaskResponse)
async def ai_complete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: bool = Depends(verify_ai_key)
):
    """Mark a task as completed (archived)"""
    result = await db.execute(
        select(Card).options(
            selectinload(Card.list).selectinload(List.board)
        ).where(Card.id == task_id)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    card.is_archived = True
    
    await db.commit()
    await db.refresh(card)
    
    return AITaskResponse(
        id=card.id,
        list_id=card.list_id,
        title=card.title,
        description=card.description,
        position=card.position,
        priority=card.priority,
        due_date=card.due_date,
        labels=card.labels,
        assigned_to=card.assigned_to,
        created_by=card.created_by,
        is_archived=card.is_archived,
        created_at=card.created_at,
        updated_at=card.updated_at,
        board_name=card.list.board.name if card.list else "Unknown",
        list_name=card.list.name if card.list else "Unknown"
    )


@router.post("/tasks/{task_id}/progress", response_model=AITaskResponse)
async def ai_update_progress(
    task_id: UUID,
    update: AITaskUpdate,
    db: AsyncSession = Depends(get_db),
    api_key: bool = Depends(verify_ai_key)
):
    """Update task progress/notes"""
    result = await db.execute(
        select(Card).options(
            selectinload(Card.list).selectinload(List.board)
        ).where(Card.id == task_id)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update description with progress notes
    if update.notes:
        if card.description:
            card.description += f"\n\n--- Progress ---\n{update.notes}"
        else:
            card.description = f"--- Progress ---\n{update.notes}"
    
    await db.commit()
    await db.refresh(card)
    
    return AITaskResponse(
        id=card.id,
        list_id=card.list_id,
        title=card.title,
        description=card.description,
        position=card.position,
        priority=card.priority,
        due_date=card.due_date,
        labels=card.labels,
        assigned_to=card.assigned_to,
        created_by=card.created_by,
        is_archived=card.is_archived,
        created_at=card.created_at,
        updated_at=card.updated_at,
        board_name=card.list.board.name if card.list else "Unknown",
        list_name=card.list.name if card.list else "Unknown"
    )
