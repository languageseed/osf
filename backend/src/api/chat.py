"""
OSF Demo - Chat API
Unified chat endpoint for all asset classes
"""

from typing import Optional, Literal
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from src.ai.core import OSFCore, AssetClass, Message

router = APIRouter()
osf_core = OSFCore()


class ChatRequest(BaseModel):
    """Chat request payload."""
    message: str
    asset_class: Literal["property", "energy"] = "property"
    role: Optional[Literal["tenant", "homeowner", "investor", "custodian", "energy_owner"]] = None
    history: Optional[list[dict]] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response payload."""
    response: str
    asset_class: str
    context_detected: Optional[str] = None


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the OSF AI Manager.
    
    Supports multiple asset classes:
    - property: Real estate (tenants, maintenance, leases)
    - energy: Solar/wind/battery (monitoring, performance, grid)
    
    Send a message and receive an AI response.
    """
    # Convert asset class
    asset_class = AssetClass(request.asset_class)
    
    # Convert history to Message objects
    history = None
    if request.history:
        history = [
            Message(role=msg.get("role", "user"), content=msg.get("content", ""))
            for msg in request.history
        ]
    
    # Detect conversation context
    context_type = await osf_core.detect_context(request.message, asset_class)
    
    # Get AI response
    response = await osf_core.chat(
        message=request.message,
        asset_class=asset_class,
        conversation_history=history,
        context=request.context,
        role=request.role,
    )
    
    return ChatResponse(
        response=response,
        asset_class=request.asset_class,
        context_detected=context_type.value,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response for real-time display.
    
    Returns Server-Sent Events (SSE) stream.
    """
    asset_class = AssetClass(request.asset_class)
    
    history = None
    if request.history:
        history = [
            Message(role=msg.get("role", "user"), content=msg.get("content", ""))
            for msg in request.history
        ]
    
    async def generate():
        async for chunk in osf_core.chat_stream(
            message=request.message,
            asset_class=asset_class,
            conversation_history=history,
            context=request.context,
            role=request.role,
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
