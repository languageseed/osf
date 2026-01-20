"""
Participant Repository
CRUD operations for network participants (users and NPCs)
"""

from decimal import Decimal
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import structlog

from src.models.network import Participant, ParticipantHolding, PendingAction

logger = structlog.get_logger()


class ParticipantRepository:
    """Repository for participant operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # =========================================================================
    # Participant CRUD
    # =========================================================================
    
    async def create(
        self,
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        role: str = "investor",
        participant_type: Optional[str] = None,
        is_npc: bool = False,
        user_id: Optional[str] = None,
        avatar_key: Optional[str] = None,
        balance: Decimal = Decimal("100000.00"),
        personality: Optional[dict] = None,
        goal: Optional[str] = None,
    ) -> Participant:
        """Create a new participant."""
        # Handle alternate parameter names
        final_name = name or display_name or "Anonymous"
        final_type = participant_type or ("npc" if is_npc else "human")
        
        participant = Participant(
            id=str(uuid4()),
            name=final_name,
            role=role,
            participant_type=final_type,
            user_id=user_id,
            avatar_key=avatar_key,
            balance=balance,
            personality=personality,
            goal=goal,
        )
        self.session.add(participant)
        await self.session.flush()
        logger.info("participant_created", id=participant.id, name=final_name, role=role, type=final_type)
        return participant
    
    async def get_by_id(self, participant_id: str) -> Optional[Participant]:
        """Get participant by ID."""
        result = await self.session.execute(
            select(Participant)
            .options(selectinload(Participant.holdings))
            .where(Participant.id == participant_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str) -> Optional[Participant]:
        """Get participant linked to a user account."""
        result = await self.session.execute(
            select(Participant)
            .options(selectinload(Participant.holdings))
            .where(Participant.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Participant]:
        """Get participant by display name."""
        result = await self.session.execute(
            select(Participant)
            .options(selectinload(Participant.holdings))
            .where(Participant.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        participant_type: Optional[str] = None,
        role: Optional[str] = None,
        is_active: bool = True,
        limit: int = 100,
    ) -> List[Participant]:
        """Get all participants with optional filters."""
        query = select(Participant).where(Participant.is_active == is_active)
        
        if participant_type:
            query = query.where(Participant.participant_type == participant_type)
        if role:
            query = query.where(Participant.role == role)
        
        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_npcs(self, limit: int = 50) -> List[Participant]:
        """Get all NPC participants."""
        return await self.get_all(participant_type="npc", limit=limit)
    
    async def get_humans(self, limit: int = 100) -> List[Participant]:
        """Get all human participants."""
        return await self.get_all(participant_type="human", limit=limit)
    
    async def update_balance(
        self,
        participant_id: str,
        amount: Decimal,
        operation: str = "add",  # add, subtract, set
    ) -> Optional[Participant]:
        """Update participant balance."""
        participant = await self.get_by_id(participant_id)
        if not participant:
            return None
        
        if operation == "add":
            participant.balance += amount
        elif operation == "subtract":
            participant.balance -= amount
        elif operation == "set":
            participant.balance = amount
        
        await self.session.flush()
        logger.info("participant_balance_updated", 
                   id=participant_id, 
                   operation=operation, 
                   amount=str(amount),
                   new_balance=str(participant.balance))
        return participant
    
    async def count(self, participant_type: Optional[str] = None) -> int:
        """Count participants."""
        from sqlalchemy import func
        query = select(func.count(Participant.id))
        if participant_type:
            query = query.where(Participant.participant_type == participant_type)
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    # =========================================================================
    # Holdings
    # =========================================================================
    
    async def add_holding(
        self,
        participant_id: str,
        property_id: str,
        token_amount: Decimal,
        purchase_price: Decimal = Decimal("1.00"),
    ) -> ParticipantHolding:
        """Add or update a token holding."""
        # Check for existing holding
        result = await self.session.execute(
            select(ParticipantHolding)
            .where(ParticipantHolding.participant_id == participant_id)
            .where(ParticipantHolding.property_id == property_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing holding with weighted average price
            total_tokens = existing.token_amount + token_amount
            existing.avg_purchase_price = (
                (existing.token_amount * existing.avg_purchase_price + token_amount * purchase_price)
                / total_tokens
            )
            existing.token_amount = total_tokens
            holding = existing
        else:
            # Create new holding
            holding = ParticipantHolding(
                id=str(uuid4()),
                participant_id=participant_id,
                property_id=property_id,
                token_amount=token_amount,
                avg_purchase_price=purchase_price,
            )
            self.session.add(holding)
        
        await self.session.flush()
        logger.info("holding_updated", 
                   participant_id=participant_id,
                   property_id=property_id,
                   tokens=str(token_amount))
        return holding
    
    async def remove_holding(
        self,
        participant_id: str,
        property_id: str,
        token_amount: Decimal,
    ) -> Optional[ParticipantHolding]:
        """Remove tokens from a holding."""
        result = await self.session.execute(
            select(ParticipantHolding)
            .where(ParticipantHolding.participant_id == participant_id)
            .where(ParticipantHolding.property_id == property_id)
        )
        holding = result.scalar_one_or_none()
        
        if not holding:
            return None
        
        if holding.token_amount <= token_amount:
            # Remove entire holding
            await self.session.delete(holding)
            return None
        else:
            holding.token_amount -= token_amount
            await self.session.flush()
            return holding
    
    async def get_holdings(self, participant_id: str) -> List[ParticipantHolding]:
        """Get all holdings for a participant."""
        result = await self.session.execute(
            select(ParticipantHolding)
            .where(ParticipantHolding.participant_id == participant_id)
        )
        return list(result.scalars().all())
    
    # =========================================================================
    # Actions
    # =========================================================================
    
    async def queue_action(
        self,
        participant_id: str,
        action_type: str,
        action_data: dict,
        network_month: int,
        priority: int = 5,
    ) -> PendingAction:
        """Queue an action for the next batch tick."""
        action = PendingAction(
            id=str(uuid4()),
            participant_id=participant_id,
            action_type=action_type,
            action_data=action_data,
            priority=priority,
            queued_for_month=network_month,
        )
        self.session.add(action)
        await self.session.flush()
        logger.info("action_queued", 
                   id=action.id,
                   participant_id=participant_id,
                   action_type=action_type)
        return action
    
    async def get_pending_actions(self, network_month: int) -> List[PendingAction]:
        """Get all pending actions for a specific month."""
        result = await self.session.execute(
            select(PendingAction)
            .where(PendingAction.status == "pending")
            .where(PendingAction.queued_for_month == network_month)
            .order_by(PendingAction.priority.desc(), PendingAction.queued_at)
        )
        return list(result.scalars().all())
    
    async def complete_action(
        self,
        action_id: str,
        result: dict,
        error: Optional[str] = None,
    ) -> Optional[PendingAction]:
        """Mark an action as completed."""
        from datetime import datetime
        
        query_result = await self.session.execute(
            select(PendingAction).where(PendingAction.id == action_id)
        )
        action = query_result.scalar_one_or_none()
        
        if not action:
            return None
        
        action.status = "failed" if error else "completed"
        action.result = result
        action.error = error
        action.processed_at = datetime.utcnow()
        
        await self.session.flush()
        return action
