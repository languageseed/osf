"""
Network Repository
CRUD operations for network state, snapshots, and events
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.models.network import NetworkSnapshot, NetworkEvent

logger = structlog.get_logger()


class NetworkRepository:
    """Repository for network-level operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # =========================================================================
    # Snapshots
    # =========================================================================
    
    async def create_snapshot(
        self,
        network_month: int,
        total_properties: int = 0,
        total_participants: int = 0,
        total_valuation: Decimal = Decimal("0"),
        total_tokens_issued: Decimal = Decimal("0"),
        avg_token_price: Decimal = Decimal("1.00"),
        avg_yield: Decimal = Decimal("4.2"),
        actions_processed: int = 0,
        tokens_traded: Decimal = Decimal("0"),
        dividends_paid: Decimal = Decimal("0"),
        rent_collected: Decimal = Decimal("0"),
        full_state: Optional[dict] = None,
        batch_response: Optional[dict] = None,
        governor_summary: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
    ) -> NetworkSnapshot:
        """Create a snapshot of the network state."""
        snapshot = NetworkSnapshot(
            id=str(uuid4()),
            network_month=network_month,
            total_properties=total_properties,
            total_participants=total_participants,
            total_valuation=total_valuation,
            total_tokens_issued=total_tokens_issued,
            avg_token_price=avg_token_price,
            avg_yield=avg_yield,
            actions_processed=actions_processed,
            tokens_traded=tokens_traded,
            dividends_paid=dividends_paid,
            rent_collected=rent_collected,
            full_state=full_state,
            batch_response=batch_response,
            governor_summary=governor_summary,
            processing_time_ms=processing_time_ms,
        )
        self.session.add(snapshot)
        await self.session.flush()
        logger.info("snapshot_created", month=network_month)
        return snapshot
    
    async def get_snapshot(self, network_month: int) -> Optional[NetworkSnapshot]:
        """Get snapshot for a specific month."""
        result = await self.session.execute(
            select(NetworkSnapshot)
            .where(NetworkSnapshot.network_month == network_month)
        )
        return result.scalar_one_or_none()
    
    async def get_latest_snapshot(self) -> Optional[NetworkSnapshot]:
        """Get the most recent snapshot."""
        result = await self.session.execute(
            select(NetworkSnapshot)
            .order_by(NetworkSnapshot.network_month.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_snapshots(
        self,
        from_month: Optional[int] = None,
        to_month: Optional[int] = None,
        limit: int = 12,
    ) -> List[NetworkSnapshot]:
        """Get snapshots with optional range filter."""
        query = select(NetworkSnapshot)
        
        if from_month is not None:
            query = query.where(NetworkSnapshot.network_month >= from_month)
        if to_month is not None:
            query = query.where(NetworkSnapshot.network_month <= to_month)
        
        query = query.order_by(NetworkSnapshot.network_month.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_current_month(self) -> int:
        """Get the current network month from latest snapshot."""
        snapshot = await self.get_latest_snapshot()
        return snapshot.network_month if snapshot else 0
    
    # =========================================================================
    # Events
    # =========================================================================
    
    async def create_event(
        self,
        network_month: int,
        event_type: str,
        title: str,
        description: str,
        severity: str = "info",
        participant_id: Optional[str] = None,
        property_id: Optional[str] = None,
        data: Optional[dict] = None,
    ) -> NetworkEvent:
        """Create a network event."""
        event = NetworkEvent(
            id=str(uuid4()),
            network_month=network_month,
            event_type=event_type,
            title=title,
            description=description,
            severity=severity,
            participant_id=participant_id,
            property_id=property_id,
            data=data,
        )
        self.session.add(event)
        await self.session.flush()
        logger.info("event_created", 
                   month=network_month, 
                   type=event_type, 
                   title=title)
        return event
    
    async def get_events(
        self,
        network_month: Optional[int] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
    ) -> List[NetworkEvent]:
        """Get events with optional filters."""
        query = select(NetworkEvent)
        
        if network_month is not None:
            query = query.where(NetworkEvent.network_month == network_month)
        if event_type:
            query = query.where(NetworkEvent.event_type == event_type)
        if severity:
            query = query.where(NetworkEvent.severity == severity)
        
        query = query.order_by(NetworkEvent.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_recent_events(self, limit: int = 20) -> List[NetworkEvent]:
        """Get most recent events across all months."""
        result = await self.session.execute(
            select(NetworkEvent)
            .order_by(NetworkEvent.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_events(
        self,
        network_month: Optional[int] = None,
        event_type: Optional[str] = None,
    ) -> int:
        """Count events."""
        query = select(func.count(NetworkEvent.id))
        if network_month is not None:
            query = query.where(NetworkEvent.network_month == network_month)
        if event_type:
            query = query.where(NetworkEvent.event_type == event_type)
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    # =========================================================================
    # Metrics
    # =========================================================================
    
    async def get_metrics_history(
        self,
        months: int = 12,
    ) -> List[dict]:
        """Get historical metrics from snapshots."""
        snapshots = await self.get_snapshots(limit=months)
        return [
            {
                "month": s.network_month,
                "total_properties": s.total_properties,
                "total_participants": s.total_participants,
                "total_valuation": float(s.total_valuation),
                "avg_token_price": float(s.avg_token_price),
                "avg_yield": float(s.avg_yield),
                "actions_processed": s.actions_processed,
                "dividends_paid": float(s.dividends_paid),
            }
            for s in reversed(snapshots)
        ]
