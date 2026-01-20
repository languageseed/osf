"""
Participant API Endpoints
User-participant management for the simulation
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import structlog

from src.services.participant_service import (
    get_or_create_participant,
    get_participant_by_user,
    update_participant_role,
    update_participant_avatar,
    get_participant_portfolio,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/participant", tags=["Participants"])


# =============================================================================
# Request/Response Models
# =============================================================================

class ParticipantResponse(BaseModel):
    """Participant data."""
    id: str
    name: str
    role: str
    participant_type: str
    avatar_key: Optional[str] = None
    balance: float
    total_invested: float
    total_dividends: float
    is_active: bool


class CreateParticipantRequest(BaseModel):
    """Request to create/link a participant."""
    user_id: str
    email: str
    display_name: Optional[str] = None
    role: str = "investor"
    avatar_key: Optional[str] = None


class UpdateRoleRequest(BaseModel):
    """Request to update participant role."""
    role: str


class UpdateAvatarRequest(BaseModel):
    """Request to update participant avatar."""
    avatar_key: str


class HoldingResponse(BaseModel):
    """Token holding."""
    property_id: str
    token_amount: float
    avg_purchase_price: float
    ownership_percent: float


class PortfolioResponse(BaseModel):
    """Complete portfolio."""
    participant_id: str
    name: str
    role: str
    balance: float
    total_invested: float
    total_dividends: float
    holdings: List[HoldingResponse]


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/", response_model=ParticipantResponse)
async def create_or_get_participant(request: CreateParticipantRequest):
    """Create or get participant for a user."""
    try:
        participant = await get_or_create_participant(
            user_id=request.user_id,
            email=request.email,
            display_name=request.display_name,
            role=request.role,
            avatar_key=request.avatar_key,
        )
        
        return ParticipantResponse(
            id=participant.id,
            name=participant.name,
            role=participant.role,
            participant_type=participant.participant_type,
            avatar_key=participant.avatar_key,
            balance=float(participant.balance),
            total_invested=float(participant.total_invested),
            total_dividends=float(participant.total_dividends),
            is_active=participant.is_active,
        )
    except Exception as e:
        logger.error("create_participant_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=ParticipantResponse)
async def get_participant(user_id: str):
    """Get participant for a user."""
    participant = await get_participant_by_user(user_id)
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return ParticipantResponse(
        id=participant.id,
        name=participant.name,
        role=participant.role,
        participant_type=participant.participant_type,
        avatar_key=participant.avatar_key,
        balance=float(participant.balance),
        total_invested=float(participant.total_invested),
        total_dividends=float(participant.total_dividends),
        is_active=participant.is_active,
    )


@router.put("/{user_id}/role", response_model=ParticipantResponse)
async def update_role(user_id: str, request: UpdateRoleRequest):
    """Update participant's role."""
    participant = await update_participant_role(user_id, request.role)
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return ParticipantResponse(
        id=participant.id,
        name=participant.name,
        role=participant.role,
        participant_type=participant.participant_type,
        avatar_key=participant.avatar_key,
        balance=float(participant.balance),
        total_invested=float(participant.total_invested),
        total_dividends=float(participant.total_dividends),
        is_active=participant.is_active,
    )


@router.put("/{user_id}/avatar", response_model=ParticipantResponse)
async def update_avatar(user_id: str, request: UpdateAvatarRequest):
    """Update participant's avatar."""
    participant = await update_participant_avatar(user_id, request.avatar_key)
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return ParticipantResponse(
        id=participant.id,
        name=participant.name,
        role=participant.role,
        participant_type=participant.participant_type,
        avatar_key=participant.avatar_key,
        balance=float(participant.balance),
        total_invested=float(participant.total_invested),
        total_dividends=float(participant.total_dividends),
        is_active=participant.is_active,
    )


@router.get("/{user_id}/portfolio", response_model=PortfolioResponse)
async def get_portfolio(user_id: str):
    """Get participant's complete portfolio."""
    portfolio = await get_participant_portfolio(user_id)
    
    if "error" in portfolio:
        raise HTTPException(status_code=404, detail=portfolio["error"])
    
    return PortfolioResponse(
        participant_id=portfolio["participant_id"],
        name=portfolio["name"],
        role=portfolio["role"],
        balance=portfolio["balance"],
        total_invested=portfolio["total_invested"],
        total_dividends=portfolio["total_dividends"],
        holdings=[
            HoldingResponse(**h) for h in portfolio["holdings"]
        ],
    )
