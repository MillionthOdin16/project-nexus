"""
Notes endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.sqlmodels import Note, Board, User
from app.models.schemas import NoteCreate, NoteUpdate, NoteResponse
from app.core.security import get_current_user
from app.api.v1.endpoints.lists import check_board_access

router = APIRouter()


@router.get("/board/{board_id}", response_model=List[NoteResponse])
async def list_notes(
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all notes for a board"""
    # Check board access
    has_access = await check_board_access(board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this board"
        )
    
    result = await db.execute(
        select(Note).where(Note.board_id == board_id).order_by(Note.created_at)
    )
    notes = result.scalars().all()
    return notes


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new note"""
    # Check board access
    has_access = await check_board_access(note_data.board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create notes in this board"
        )
    
    note = Note(
        board_id=note_data.board_id,
        title=note_data.title,
        content=note_data.content,
        position=note_data.position,
        created_by=current_user.id
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a note"""
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Check board access
    has_access = await check_board_access(note.board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this note"
        )
    
    # Update fields
    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content
    if note_data.position is not None:
        note.position = note_data.position
    
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a note"""
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Check board access
    has_access = await check_board_access(note.board_id, current_user.id, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this note"
        )
    
    await db.delete(note)
    await db.commit()
    return None
