"""Data models for Copilot Chat."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Represents a single chat message"""
    id: str
    timestamp: datetime
    role: str  # 'user' or 'assistant'
    content: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatSession(BaseModel):
    """Represents a chat session"""
    session_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = Field(default_factory=list)
