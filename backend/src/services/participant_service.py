"""
Participant Service
Manages the connection between users and their simulation participants
"""

from decimal import Decimal
from typing import Optional
import structlog

from src.database import async_session
from src.repositories.participant import ParticipantRepository
from src.models.network import Participant

logger = structlog.get_logger()


async def get_or_create_participant(
    user_id: str,
    email: str,
    display_name: Optional[str] = None,
    role: str = "investor",
    avatar_key: Optional[str] = None,
) -> Participant:
    """
    Get existing participant for a user or create a new one.
    Called during authentication to ensure user has a simulation participant.
    """
    async with async_session() as session:
        repo = ParticipantRepository(session)
        
        # Check for existing participant
        participant = await repo.get_by_user_id(user_id)
        
        if participant:
            logger.info("participant_found", user_id=user_id, participant_id=participant.id)
            return participant
        
        # Create new participant
        name = display_name or email.split("@")[0]
        participant = await repo.create(
            name=name,
            role=role,
            participant_type="human",
            user_id=user_id,
            avatar_key=avatar_key,
            balance=Decimal("100000.00"),  # Starting balance
        )
        
        await session.commit()
        logger.info("participant_created", 
                   user_id=user_id, 
                   participant_id=participant.id,
                   name=name)
        return participant


async def get_participant_by_user(user_id: str) -> Optional[Participant]:
    """Get participant for a user."""
    async with async_session() as session:
        repo = ParticipantRepository(session)
        return await repo.get_by_user_id(user_id)


async def update_participant_role(
    user_id: str,
    new_role: str,
) -> Optional[Participant]:
    """Update participant's role."""
    async with async_session() as session:
        repo = ParticipantRepository(session)
        participant = await repo.get_by_user_id(user_id)
        
        if not participant:
            return None
        
        participant.role = new_role
        await session.commit()
        
        logger.info("participant_role_updated", 
                   user_id=user_id, 
                   new_role=new_role)
        return participant


async def update_participant_avatar(
    user_id: str,
    avatar_key: str,
) -> Optional[Participant]:
    """Update participant's avatar."""
    async with async_session() as session:
        repo = ParticipantRepository(session)
        participant = await repo.get_by_user_id(user_id)
        
        if not participant:
            return None
        
        participant.avatar_key = avatar_key
        await session.commit()
        
        logger.info("participant_avatar_updated", 
                   user_id=user_id, 
                   avatar_key=avatar_key)
        return participant


async def get_participant_portfolio(user_id: str) -> dict:
    """Get participant's complete portfolio."""
    async with async_session() as session:
        repo = ParticipantRepository(session)
        participant = await repo.get_by_user_id(user_id)
        
        if not participant:
            return {"error": "Participant not found"}
        
        holdings = await repo.get_holdings(participant.id)
        
        return {
            "participant_id": participant.id,
            "name": participant.name,
            "role": participant.role,
            "balance": float(participant.balance),
            "total_invested": float(participant.total_invested),
            "total_dividends": float(participant.total_dividends),
            "holdings": [
                {
                    "property_id": h.property_id,
                    "token_amount": float(h.token_amount),
                    "avg_purchase_price": float(h.avg_purchase_price),
                    "ownership_percent": float(h.ownership_percent),
                }
                for h in holdings
            ],
        }
