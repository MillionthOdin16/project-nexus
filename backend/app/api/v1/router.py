"""
API v1 router - main router file
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, boards, lists, cards, notes, comments, ai

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(boards.router, prefix="/boards", tags=["Boards"])
api_router.include_router(lists.router, prefix="/lists", tags=["Lists"])
api_router.include_router(cards.router, prefix="/cards", tags=["Cards"])
api_router.include_router(notes.router, prefix="/notes", tags=["Notes"])
api_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
