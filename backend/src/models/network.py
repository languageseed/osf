"""
OSF Network State Models
Persistence for simulation state, participants, and actions
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Numeric, DateTime, ForeignKey, Integer, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Participant(Base):
    """Network participant - can be human user or NPC."""
    __tablename__ = "participants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Link to user (null for NPCs)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("sim_users.id"), nullable=True)
    
    # Participant info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    participant_type: Mapped[str] = mapped_column(String(20), default="human")  # human, npc
    role: Mapped[str] = mapped_column(String(50), default="investor")  # investor, renter, homeowner, service, foundation
    avatar_key: Mapped[Optional[str]] = mapped_column(String(50))  # Key to avatar pool
    
    # Financial state
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("100000.00"))
    total_invested: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    total_dividends: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    
    # NPC personality (JSON for flexibility)
    personality: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    goal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_action_month: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holdings: Mapped[list["ParticipantHolding"]] = relationship(back_populates="participant", cascade="all, delete-orphan")
    actions: Mapped[list["PendingAction"]] = relationship(back_populates="participant", cascade="all, delete-orphan")


class ParticipantHolding(Base):
    """Participant's token holdings in a property."""
    __tablename__ = "participant_holdings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    participant_id: Mapped[str] = mapped_column(String(36), ForeignKey("participants.id"), nullable=False)
    property_id: Mapped[str] = mapped_column(String(36), nullable=False)  # References pool property
    
    token_amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    avg_purchase_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("1.00"))
    
    # Ownership percentage of property
    ownership_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participant: Mapped["Participant"] = relationship(back_populates="holdings")


class PendingAction(Base):
    """Queued user action waiting for next batch tick."""
    __tablename__ = "pending_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    participant_id: Mapped[str] = mapped_column(String(36), ForeignKey("participants.id"), nullable=False)
    
    # Action details
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)  # buy, sell, rent, vote, service, chat
    action_data: Mapped[dict] = mapped_column(JSON, nullable=False)  # Action-specific data
    priority: Mapped[int] = mapped_column(Integer, default=5)  # Higher = processed first
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processing, completed, failed
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Result after processing
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    queued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    queued_for_month: Mapped[int] = mapped_column(Integer, nullable=False)  # Network month when queued
    
    # Relationships
    participant: Mapped["Participant"] = relationship(back_populates="actions")


class NetworkSnapshot(Base):
    """Snapshot of network state at end of each month."""
    __tablename__ = "network_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Network month this snapshot represents
    network_month: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    
    # Summary metrics
    total_properties: Mapped[int] = mapped_column(Integer, default=0)
    total_participants: Mapped[int] = mapped_column(Integer, default=0)
    total_valuation: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    total_tokens_issued: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("0"))
    avg_token_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("1.00"))
    avg_yield: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("4.2"))
    
    # Activity metrics for this month
    actions_processed: Mapped[int] = mapped_column(Integer, default=0)
    tokens_traded: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("0"))
    dividends_paid: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    rent_collected: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    
    # Full state snapshot (for recovery/replay)
    full_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Gemini batch response
    batch_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    governor_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class NetworkEvent(Base):
    """Events generated during simulation."""
    __tablename__ = "network_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Event details
    network_month: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # trade, dividend, rent, governance, market, maintenance
    severity: Mapped[str] = mapped_column(String(20), default="info")  # info, warning, alert, critical
    
    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Related entities
    participant_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    property_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Event data
    data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PropertyState(Base):
    """Current state of a property in the network."""
    __tablename__ = "property_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # Same as pool property ID
    
    # Status in simulation
    status: Mapped[str] = mapped_column(String(20), default="available")  # available, tenanted, sold
    enabled_at_month: Mapped[int] = mapped_column(Integer, default=0)
    
    # Token economics
    total_tokens: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("100000"))
    tokens_available: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("100000"))
    token_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("1.00"))
    network_ownership: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))  # % owned by network
    
    # Rental state
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    weekly_rent: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    lease_start_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lease_end_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Financials
    total_rent_collected: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    total_dividends_paid: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    maintenance_reserve: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    
    # Valuation history (last update)
    current_valuation: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    last_valuation_month: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
