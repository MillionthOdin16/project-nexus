"""
SQLAlchemy models for Project Nexus
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, Text, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owned_boards = relationship("Board", back_populates="owner", foreign_keys="Board.owner_id")
    board_memberships = relationship("BoardMember", back_populates="user")
    created_cards = relationship("Card", back_populates="creator", foreign_keys="Card.created_by")
    assigned_cards = relationship("Card", back_populates="assignee", foreign_keys="Card.assigned_to")
    comments = relationship("Comment", back_populates="author")
    notes = relationship("Note", back_populates="creator")
    activities = relationship("ActivityLog", back_populates="user")


class Board(Base):
    __tablename__ = "boards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_shared = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="owned_boards", foreign_keys=[owner_id])
    members = relationship("BoardMember", back_populates="board", cascade="all, delete-orphan")
    lists = relationship("List", back_populates="board", cascade="all, delete-orphan", order_by="List.position")
    notes = relationship("Note", back_populates="board", cascade="all, delete-orphan")
    activities = relationship("ActivityLog", back_populates="board", cascade="all, delete-orphan")


class BoardMember(Base):
    __tablename__ = "board_members"
    
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(String(50), default="member")  # admin, member, viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    board = relationship("Board", back_populates="members")
    user = relationship("User", back_populates="board_memberships")


class List(Base):
    __tablename__ = "lists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    position = Column(Integer, default=0)
    color = Column(String(7), nullable=True)  # hex color
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    board = relationship("Board", back_populates="lists")
    cards = relationship("Card", back_populates="list", cascade="all, delete-orphan", order_by="Card.position")


class Card(Base):
    __tablename__ = "cards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    list_id = Column(UUID(as_uuid=True), ForeignKey("lists.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    position = Column(Integer, default=0)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    due_date = Column(DateTime, nullable=True)
    labels = Column(JSONB, default=list)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    list = relationship("List", back_populates="cards")
    creator = relationship("User", back_populates="created_cards", foreign_keys=[created_by])
    assignee = relationship("User", back_populates="assigned_cards", foreign_keys=[assigned_to])
    comments = relationship("Comment", back_populates="card", cascade="all, delete-orphan")
    activities = relationship("ActivityLog", back_populates="card", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    position = Column(JSON, nullable=True)  # For free-form canvas positioning
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    board = relationship("Board", back_populates="notes")
    creator = relationship("User", back_populates="notes")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    card = relationship("Card", back_populates="comments")
    author = relationship("User", back_populates="comments")


class ActivityLog(Base):
    __tablename__ = "activity_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), nullable=True)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    board = relationship("Board", back_populates="activities")
    card = relationship("Card", back_populates="activities")
    user = relationship("User", back_populates="activities")
