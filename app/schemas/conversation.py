"""
Conversation and Message Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.core.constants import ConversationState, MessageDirection, MessageProcessingStatus, MessageType


class MessageBase(BaseModel):
    direction: MessageDirection = Field(MessageDirection.INBOUND)
    message_type: MessageType = Field(MessageType.TEXT)
    content: str = Field(..., min_length=1)
    external_message_id: Optional[str] = Field(None, description="Meta WhatsApp message ID (wamid)")
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class MessageCreate(MessageBase):
    conversation_id: uuid.UUID


class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    status: MessageProcessingStatus
    created_at: datetime


class ConversationBase(BaseModel):
    lead_id: uuid.UUID
    channel: str = Field("whatsapp")
    state: ConversationState = Field(ConversationState.NEW_ENQUIRY)
    is_human_takeover: bool = Field(False)


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    last_message_at: datetime
    created_at: datetime
    messages: List[MessageResponse] = []
