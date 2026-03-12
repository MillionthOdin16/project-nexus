from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Task, Board, User, TaskStatus
from app.schemas import TaskCreate, TaskUpdate, Task as TaskSchema, TaskWithAssignee, TaskMove
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TaskWithAssignee])
def get_tasks(board_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Task).join(Board).filter(Board.owner_id == current_user.id)
    if board_id:
        query = query.filter(Task.board_id == board_id)
    return query.all()

@router.post("/", response_model=TaskSchema)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == task.board_id, Board.owner_id == current_user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Get max position for the status column
    max_position = db.query(Task).filter(Task.board_id == task.board_id, Task.status == task.status).count()
    
    db_task = Task(**task.dict(), created_by=current_user.id, position=max_position)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/{task_id}", response_model=TaskWithAssignee)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).join(Board).filter(Task.id == task_id, Board.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskSchema)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).join(Board).filter(Task.id == task_id, Board.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.patch("/{task_id}/move", response_model=TaskSchema)
def move_task(task_id: int, move: TaskMove, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).join(Board).filter(Task.id == task_id, Board.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = move.status
    task.position = move.position
    
    if move.status == TaskStatus.DONE:
        task.completed_at = datetime.utcnow()
    else:
        task.completed_at = None
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).join(Board).filter(Task.id == task_id, Board.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
