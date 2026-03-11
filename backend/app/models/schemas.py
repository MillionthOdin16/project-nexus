"""
Pydantic schemas for API request/response validation
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# Board schemas
class BoardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_shared: Optional[bool] = None


class BoardResponse(BoardBase):
    id: UUID
    owner_id: UUID
    is_shared: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BoardWithLists(BoardResponse):
    lists: List["ListResponse"] = []
    
    class Config:
        from_attributes = True


# List schemas
class ListBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    color: Optional[str] = None


class ListCreate(ListBase):
    position: Optional[int] = 0


class ListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    color: Optional[str] = None
    position: Optional[int] = None


class ListResponse(ListBase):
    id: UUID
    board_id: UUID
    position: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ListWithCards(ListResponse):
    cards: List["CardResponse"] = []
    
    class Config:
        from_attributes = True


# Card schemas
class CardBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    priority: str = Field(default="medium")
    due_date: Optional[datetime] = None
    labels: Optional[List[dict]] = []


class CardCreate(CardBase):
    list_id: UUID
    position: Optional[int] = 0


class CardUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    labels: Optional[List[dict]] = None
    assigned_to: Optional[UUID] = None
    is_archived: Optional[bool] = None


class CardMove(BaseModel):
    list_id: UUID
    position: int


class CardResponse(CardBase):
    id: UUID
    list_id: UUID
    position: int
    assigned_to: Optional[UUID] = None
    created_by: UUID
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Note schemas
class NoteBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    position: Optional[dict] = None


class NoteCreate(NoteBase):
    board_id: UUID


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    position: Optional[dict] = None


class NoteResponse(NoteBase):
    id: UUID
    board_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Comment schemas
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    card_id: UUID


class CommentResponse(CommentBase):
    id: UUID
    card_id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Activity Log schemas
class ActivityLogResponse(BaseModel):
    id: UUID
    board_id: Optional[UUID] = None
    card_id: Optional[UUID] = None
    user_id: UUID
    action: str
    details: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# AI API schemas
class AITaskResponse(CardResponse):
    board_name: str
    list_name: str
    
    class Config:
        from_attributes = True


class AITaskUpdate(BaseModel):
    status: str  # in_progress, completed, blocked
    notes: Optional[str] = None


# Reorder schemas
class ReorderItems(BaseModel):
    items: List[dict]  # [{"id": "uuid", "position": 0}]


# Update forward refs
ListWithCards.model_rebuild()
