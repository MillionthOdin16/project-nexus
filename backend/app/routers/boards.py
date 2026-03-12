from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Board, User
from app.schemas import BoardCreate, Board as BoardSchema, BoardWithTasks
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[BoardSchema])
def get_boards(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Board).filter(Board.owner_id == current_user.id).all()

@router.post("/", response_model=BoardSchema)
def create_board(board: BoardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_board = Board(**board.dict(), owner_id=current_user.id)
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board

@router.get("/{board_id}", response_model=BoardWithTasks)
def get_board(board_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == board_id, Board.owner_id == current_user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.put("/{board_id}", response_model=BoardSchema)
def update_board(board_id: int, board: BoardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_board = db.query(Board).filter(Board.id == board_id, Board.owner_id == current_user.id).first()
    if not db_board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    for key, value in board.dict().items():
        setattr(db_board, key, value)
    
    db.commit()
    db.refresh(db_board)
    return db_board

@router.delete("/{board_id}")
def delete_board(board_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == board_id, Board.owner_id == current_user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    db.delete(board)
    db.commit()
    return {"message": "Board deleted"}
