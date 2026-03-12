from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

from app.database import get_db
from app.models import Task, Board, TaskStatus
from app.schemas import AITaskResponse, AIClaimRequest, AICompleteRequest

router = APIRouter()

AI_API_KEY = os.getenv("AI_API_KEY", "")

def verify_ai_key(x_api_key: Optional[str] = Header(None)):
    if not AI_API_KEY:
        raise HTTPException(status_code=503, detail="AI API not configured")
    if x_api_key != AI_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@router.get("/tasks", response_model=List[AITaskResponse])
def get_available_tasks(db: Session = Depends(get_db), api_key: str = Depends(verify_ai_key)):
    """Get tasks that are ready for AI processing (in todo or backlog status)"""
    tasks = db.query(Task).filter(
        Task.status.in_([TaskStatus.BACKLOG, TaskStatus.TODO]),
        Task.claimed_by_ai == False
    ).all()
    return tasks

@router.post("/tasks/{task_id}/claim")
def claim_task(task_id: int, claim: AIClaimRequest, db: Session = Depends(get_db), api_key: str = Depends(verify_ai_key)):
    """Claim a task for AI processing"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.claimed_by_ai:
        raise HTTPException(status_code=400, detail="Task already claimed")
    
    task.claimed_by_ai = True
    task.ai_agent_id = claim.agent_id
    task.status = TaskStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(task)
    return {"message": "Task claimed", "task_id": task_id, "agent_id": claim.agent_id}

@router.post("/tasks/{task_id}/complete")
def complete_task(task_id: int, complete: AICompleteRequest, db: Session = Depends(get_db), api_key: str = Depends(verify_ai_key)):
    """Mark an AI-claimed task as complete"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.claimed_by_ai:
        raise HTTPException(status_code=400, detail="Task not claimed by AI")
    
    task.status = TaskStatus.DONE
    task.completed_at = datetime.utcnow()
    # Append result to description
    task.description = f"{task.description or ''}\n\n[AI Result]: {complete.result}".strip()
    
    db.commit()
    db.refresh(task)
    return {"message": "Task completed", "task_id": task_id}
