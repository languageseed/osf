"""
Property State Repository
CRUD operations for property states in the simulation
"""

from decimal import Decimal
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.models.network import PropertyState

logger = structlog.get_logger()


class PropertyStateRepository:
    """Repository for property state operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_or_update(
        self,
        property_id: str,
        status: str = "available",
        enabled_at_month: int = 0,
        total_tokens: Decimal = Decimal("100000"),
        token_price: Decimal = Decimal("1.00"),
        current_valuation: Decimal = Decimal("0"),
        weekly_rent: Decimal = Decimal("0"),
    ) -> PropertyState:
        """Create or update a property state."""
        # Check for existing
        result = await self.session.execute(
            select(PropertyState).where(PropertyState.id == property_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.status = status
            existing.token_price = token_price
            existing.current_valuation = current_valuation
            existing.weekly_rent = weekly_rent
            state = existing
        else:
            state = PropertyState(
                id=property_id,
                status=status,
                enabled_at_month=enabled_at_month,
                total_tokens=total_tokens,
                tokens_available=total_tokens,
                token_price=token_price,
                current_valuation=current_valuation,
                weekly_rent=weekly_rent,
            )
            self.session.add(state)
        
        await self.session.flush()
        logger.info("property_state_saved", id=property_id, status=status)
        return state
    
    async def get_by_id(self, property_id: str) -> Optional[PropertyState]:
        """Get property state by ID."""
        result = await self.session.execute(
            select(PropertyState).where(PropertyState.id == property_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[PropertyState]:
        """Get all property states."""
        query = select(PropertyState)
        if status:
            query = query.where(PropertyState.status == status)
        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_available(self, limit: int = 50) -> List[PropertyState]:
        """Get available properties for investment."""
        return await self.get_all(status="available", limit=limit)
    
    async def get_tenanted(self, limit: int = 50) -> List[PropertyState]:
        """Get tenanted properties."""
        return await self.get_all(status="tenanted", limit=limit)
    
    async def update_tokens(
        self,
        property_id: str,
        tokens_sold: Decimal,
        new_price: Optional[Decimal] = None,
    ) -> Optional[PropertyState]:
        """Update token availability after a trade."""
        state = await self.get_by_id(property_id)
        if not state:
            return None
        
        state.tokens_available -= tokens_sold
        state.network_ownership = (
            (state.total_tokens - state.tokens_available) / state.total_tokens * 100
        )
        
        if new_price:
            state.token_price = new_price
        
        await self.session.flush()
        logger.info("property_tokens_updated",
                   id=property_id,
                   sold=str(tokens_sold),
                   available=str(state.tokens_available),
                   ownership=str(state.network_ownership))
        return state
    
    async def set_tenant(
        self,
        property_id: str,
        tenant_id: str,
        weekly_rent: Decimal,
        lease_start_month: int,
        lease_end_month: int,
    ) -> Optional[PropertyState]:
        """Set tenant for a property."""
        state = await self.get_by_id(property_id)
        if not state:
            return None
        
        state.status = "tenanted"
        state.tenant_id = tenant_id
        state.weekly_rent = weekly_rent
        state.lease_start_month = lease_start_month
        state.lease_end_month = lease_end_month
        
        await self.session.flush()
        logger.info("property_tenant_set",
                   id=property_id,
                   tenant_id=tenant_id,
                   weekly_rent=str(weekly_rent))
        return state
    
    async def clear_tenant(self, property_id: str) -> Optional[PropertyState]:
        """Remove tenant from property."""
        state = await self.get_by_id(property_id)
        if not state:
            return None
        
        state.status = "available"
        state.tenant_id = None
        state.lease_start_month = None
        state.lease_end_month = None
        
        await self.session.flush()
        logger.info("property_tenant_cleared", id=property_id)
        return state
    
    async def record_rent(
        self,
        property_id: str,
        amount: Decimal,
    ) -> Optional[PropertyState]:
        """Record rent collection."""
        state = await self.get_by_id(property_id)
        if not state:
            return None
        
        state.total_rent_collected += amount
        await self.session.flush()
        return state
    
    async def record_dividend(
        self,
        property_id: str,
        amount: Decimal,
    ) -> Optional[PropertyState]:
        """Record dividend payment."""
        state = await self.get_by_id(property_id)
        if not state:
            return None
        
        state.total_dividends_paid += amount
        await self.session.flush()
        return state
    
    async def count(self, status: Optional[str] = None) -> int:
        """Count properties."""
        query = select(func.count(PropertyState.id))
        if status:
            query = query.where(PropertyState.status == status)
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def get_total_valuation(self) -> Decimal:
        """Get total valuation of all properties."""
        result = await self.session.execute(
            select(func.sum(PropertyState.current_valuation))
        )
        return result.scalar() or Decimal("0")
