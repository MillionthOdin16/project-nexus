from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models import TaskStatus, TaskPriority

# User schemas
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Board schemas
class BoardBase(BaseModel):
    title: str
    description: Optional[str] = None

class BoardCreate(BoardBase):
    pass

class Board(BoardBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BoardWithTasks(Board):
    tasks: List["Task"] = []

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.BACKLOG
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    labels: Optional[str] = None

class TaskCreate(TaskBase):
    board_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    labels: Optional[str] = None
    assignee_id: Optional[int] = None

class TaskMove(BaseModel):
    status: TaskStatus
    position: int

class Task(TaskBase):
    id: int
    board_id: int
    assignee_id: Optional[int]
    created_by: int
    position: int
    claimed_by_ai: bool
    ai_agent_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class TaskWithAssignee(Task):
    assignee: Optional[User] = None

# AI schemas
class AITaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: TaskPriority
    board_id: int

class AIClaimRequest(BaseModel):
    agent_id: str

class AICompleteRequest(BaseModel):
    result: str
